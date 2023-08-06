import os
import sys
import json
import glob
import time
import copy
import traceback
import tempfile
import shutil
import numpy as np
import pandas as pd
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
import logging
import s3fs
from dateutil import parser as dateparser

from enrichsdk.contrib.lib.transforms import MetricsBase
from enrichsdk.lib.integration import send_html_email
from enrichsdk.utils import (note, get_today, get_yesterday, get_tomorrow)

# Define a registry
from libtip.datasets import get_registry

logger = logging.getLogger("app")
thisdir = os.path.dirname(__file__)

from .profilespec import get_profile_spec

class My{{transform_name}}(S3Mixin, MetricsBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "{{transform_name}}"
        self.description = "{{transform_description}}"
        self.author = "{{author_name}}"

        self.supported_extra_args = [
            {
                "name": "run_date",
                "description": "Date of execution",
                "default": get_today,
                "required": False,
            },
            {
                "name": "specs",
                "description": "specs to run (all|<add list>)",
                "default": "all",
                "required": False,
            },
            {
                "name": "send_email",
                "description": "Send daily notification email",
                "default": "false",
                "required": False,
            },
        ]

        test_root = os.environ['ENRICH_TEST']
        self.testdata = {
            'data_root': os.path.join(test_root, self.name),
            'inputdir': test_root,
            'outputdir': os.path.join(test_root, self.name, 'output'),
            'statedir': os.path.join(test_root, self.name, 'state'),
            'conf': {
                'args': {
                    "run_date": get_today(),
                    "s3cred": "demouser",
                    's3root':   "enrich-demodata/backup/%(node)s/data/acme/Core/shared/emetrics",
                    "specs": "all",
                    "receivers": {}
                }
            },
            'data': {
            }
        }

    @classmethod
    def instantiable(cls):
        return True

    def preload_clean_args(self, args):

        args = super().preload_clean_args(args)

        args['s3root'] = self.get_file(args['s3root'], abspath=False)
        args['s3cred'] = s3cred = self.get_credentials(args['s3cred'])
        args['s3'] = s3fs.S3FileSystem(anon=False,
                                       key=s3cred['access_key'],
                                       secret=s3cred['secret_key'])

        # Insert these variables...
        run_date = dateparser.parse(args['run_date']).date()
        args['run_date'] = run_date
        args['end_date'] = args['run_date'] = run_date
        args['start_date'] = args['end_date'] + timedelta(days=-31)

        return args

    #################################
    # Get data
    #################################
    def get_db_uri(self, source):
        uri = source['uri']
        uri = self.get_file(uri, abspath=False)
        return uri

    def get_profile(self):
        """
        Construct ore turn profile.
        """
        return get_profile_spec()

    def get_specs(self, profile):
        """
        Return a list of valid specifications...
        """
        # Get all available specs
        specs = super().get_specs(profile)

        # now filter them out...
        if 'all' in self.args['specs']:
            return specs

        selected = [s for s in specs if s['name'] in self.args['specs']]
        return selected

    def get_dataset(self, name):
        """
        Get dataset by
        """
        registry = get_registry(transform=self, state=self.state)
        datasetobj = registry.find(name)
        if datasetobj is None:
            raise Exception(f"Unknown dataset: {name}")
        return datasetobj

    def read_data(self, filename, params, **kwargs):

        s3 = self.args['s3']
        if s3.exists(filename):
            df = pd.read_csv(s3.open(filename),**params)

            if (('ledger_balance' in filename) or
                ('ledgers_cash_flow_analysis' in filename) or
                ('mtn' in filename)
            ):
                df['snapshot_date'] = kwargs['date']

            return df

        return None

    ##########################
    # State management
    ##########################
    def update_state(self, spec, framename, framedesc, framedf, s3path):
        """
        Save the results for profiling..
        """

        s3 = self.args['s3']

        state = self.state
        framemgr = self.config.get_dataframe('pandas')

        # Generate column information...
        params = self.get_column_params(framename, framedf)

        params.append({
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "dataframe",
                        "nature": "input",
                        "objects": spec['sources']
                    },
                    {
                        "type": "file",
                        "nature": "output",
                        "objects": [s3path]
                    }
                ]
        })

        ## => Gather the update parameters
        updated_detail = {
            'df': framedf,
            'description': framedesc,
            'transform': self.name,
            'frametype': 'pandas',
            'params': params,
            'history': [
                # Add a log entry describing the change
                {
                    'transform': self.name,
                    'log': 'Generated the dataset'
                }
            ]
        }

        # Dump it into the shared state
        state.update_frame(framename, updated_detail, create=True)

    ##############################
    # Store in S3/Other...
    ##############################
    def store_common(self, data, spec, descriptions={}):
        """
        Store in s3. This code assumes that s3 handle is
        available. Replace as required.
        """

        s3root = self.args['s3root']
        run_date = self.args['run_date']
        version = "v1"

        # Replace as required...
        s3   = self.args['s3']

        # Pipeline metadata
        metadata = self.get_default_metadata(self.state)

        # Insert column information
        columns = {}
        for name, df in data.items():
            extra = self.get_column_metadata(name, df)
            columns[name]  = extra
        metadata['columns'] = columns

        root = os.path.join(s3root, version, run_date.isoformat())
        metadatafile = os.path.join(root, f"{spec['name']}.metadata.json")

        # Now dump the data
        with s3.open(metadatafile, 'w') as fd:
            fd.write(json.dumps(metadata, indent=4))
        msg = "metadata: {}\n".format(metadatafile)

        # => Destination details...
        for name, df in data.items():
            filename = os.path.join(root, f"{spec['name']}.{name}.csv")
            msg += f"{name}: {filename}\n"
            with s3.open(filename, 'w') as fd:
                df.to_csv(fd, index=False)

            # Update the state with the dataframe...
            self.update_state(spec,
                              f"{spec['name']}-{name}",
                              descriptions.get(name,name),
                              df, filename)

        msg += '\n'
        logger.debug(f"{spec['name']} wrote to s3: {run_date.isoformat()}",
                     extra={
                         'transform': self.name,
                         'data': msg
                     })

    def send_common(self, spec, attachments, note=None):
        """
        Send email/other notifications. with required
        attachments. This is useful when the metrics needs to be
        'pushed'
        """

        run_date = self.args['run_date']
        allreceivers = self.args['receivers'].get('all', [])
        receivers = self.args['receivers'].get(spec['name'], allreceivers)
        if len(receivers) == 0:
            logger.debug(f"Skipping notifications. No receivers",
                         extra={
                             'transform': self.name,
                         })
            return

        html = f"""\
        <h2>{spec['description']} - {run_date.isoformat()}</h2>

        """
        if note is not None:
            html += note

        # Replace as required...
        sender='Analytics Team<support@scribbledata.io>'
        subject=f"{spec['description']} - {format(run_date.isoformat())}"
        send_html_email(html,
                        sender=sender,
                        receivers=receivers,
                        subject=subject,
                        attachments=attachments)

        logger.debug("Email notification sent",
                     extra={
                         'transform': self.name,
                         'data': "Receivers: " + json.dumps(receivers)
                     })

    def clean_query_result(self, df, source):

        name = source['name']
        logger.debug(f"Cleaning {name}")

        aggspec = {
            'total_txn_count': 'sum',
        }
        for col in df.columns:
            if col.endswith("_unique") or col in ['months', 'nationality_cleaned']:
                aggspec[col] = lambda s: ";".join(s.unique())

        df1 = df.groupby('unique_key').agg(aggspec)

        # Label customer as repeat customer
        df1['repeat'] = df1['total_txn_count'].map(lambda x: 1 if x > 1 else 0)

        df1 = df1.reset_index()

        return {
            "query_data_cleaned": df1
        }

    def generate_result(self, data, spec):

        df = data[spec['name']]

        # Do something complicated...
        df = df.rename(columns={
            'lifetime_mean': "lifetime_mean_days",
        })

        df = df.sort_values(['dimensions','all_customers'],  ascending=[True, False])

        # Return a set of processed dataframes
        return {
            spec['name']: df
        }

    ###########################################
    # Store in multiple forms...
    ###########################################
    def store_results_excel(self, dirname, data, spec):
        """
        Override as required..
        """
        run_date = self.args['run_date']

        filename = os.path.join(dirname, f'{spec["name"]}-{run_date.isoformat()}.xlsx')
        writer = pd.ExcelWriter(filename,engine='xlsxwriter')
        workbook=writer.book

        # Write some or all the dataframes in the data dictionary
        for name, df in data.items():
            df.to_excel(writer, sheet_name=name, startrow=0, startcol=0, index=False)

        # Write the sheets
        writer.save()

        return filename

    def store_result(self, spec, data):
        """

        """
        run_date = self.args['run_date']

        self.store_common(data, spec)

        # Should I send an email/notification:
        if not self.args['send_email']:
            logger.debug(f"Skipping sending email",
                         extra={
                             'transform': self.name
                         })
            return

        note="<p>Note: Any additional notes to add</p>"

        try:
            tmpdir = tempfile.mkdtemp()
            filename = self.store_results_excel(tmpdir, data, spec)
            self.send_common(spec, note=note, attachments=[filename])


        except:
            logger.exception("Unable to send email",
                         extra={
                             'transform': self.name,
                         })

        if os.path.exists(tmpdir):
            try:
                shutil.rmtree(tmpdir)
            except:
                logger.exception("Unable to cleanup temporary directory",
                                 extra={
                                     'transform': self.name,
                                     'data': tmpdir
                                 })


provider = My{{transform_name}}
