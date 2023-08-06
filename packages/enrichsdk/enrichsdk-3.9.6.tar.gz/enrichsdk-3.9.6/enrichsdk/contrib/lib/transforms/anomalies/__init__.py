import os
import io
import re
import numpy as np
import pandas as pd
import time
from enrichsdk import Compute, S3Mixin
from datetime import datetime, timedelta, date
from scipy.spatial import distance
import seaborn as sns
import matplotlib.pyplot as plt
import logging
from enrichsdk.contrib.lib.transforms import note

from .iofn import *

logger = logging.getLogger("app")


class AnomaliesBase(Compute):
    """
    Compute anomalies given a dataframe with columns

    Features of transform baseclass include:

        * Flexible configuration
        * Highlevel specification of columns combinations and detection strategy

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "AnomaliesBase"
        self.description = "Compute anomalies in column(s) of a dataframe"
        self.testdata = {
            "data_root": os.path.join(os.environ["ENRICH_TEST"], self.name),
            "statedir": os.path.join(os.environ["ENRICH_TEST"], self.name, "state"),
            "conf": {"args": {}},
            "data": {},
        }

    @classmethod
    def instantiable(cls):
        return False

    def get_handlers(self, spec):
        """
        Define various callbacks that take a dataframe, spec
        and compute.
        """
        return {}

    def get_profile(self):
        """
        Read the profile json from API
        """

        if (not hasattr(self, "args")):
            raise Exception(
                "'args' transform attribute should be defined to use default get_profile method"
            )
        for p in ['apiserver', 'apicred']:
            if self.args.get(p) == None:
                raise Exception(
                    f"'{p}' attribute in args should be defined to use default get_profile method"
                    )

        # call the API to get the anomaly specs
        anomalyspecs, is_valid, msg = load_profile_api(self.args)
        logger.debug(
            f"Loading profile from API",
            extra={"transform": self.name, "data": msg},
        )
        if is_valid == False:
            raise Exception(f"Error loading profile")

        specs = anomalyspecs["specs"]
        logger.debug(
            f"Found {len(specs)} specs",
            extra={"transform": self.name, "data": json.dumps(anomalyspecs, indent=4)},
        )

        return anomalyspecs

    def get_specs(self, profile):
        if (not isinstance(profile, dict)) or ("specs" not in profile):
            raise Exception("Specs not defined in profile")
        return profile["specs"]

    def process_spec(self, spec, datasets):
        msg = ""

        # check profile
        if (not isinstance(spec, dict)) or (len(spec) == 0):
            raise Exception("Spec should be a valid dict")
        for p in ["name", "desc", "config"]:
            if (p not in spec):
                err = f"Invalid spec: {p} missing"
                raise Exception(err)
        for p in ["dataset", "detect"]:
            if (p not in spec['config']):
                err = f"Invalid spec->config: {p} missing"
                raise Exception(err)

        name = spec["name"]
        config = spec["config"]
        handlers = self.get_handlers(spec)
        dataset = config["dataset"]

        # first, get the dataset nature
        nature = None
        paths = datasets[dataset].paths
        for path in paths:
            if path['name'] == 'default':
                nature = path['nature']
                break

        if nature == None:
            err = f"No nature found for dataset: {dataset}"
            raise Exception(err)

        try:
            if nature == "db":
                result = self.read_db_source(spec)
            elif nature == "s3":
                result = self.get_dataset_s3(spec, datasets)
            elif (
                (generate is not None)
                and (generate in handlers)
                and (callable(handlers[generate]))
            ):
                result = handlers[generate](spec)
            elif (generate is not None) and (hasattr(self, generate)):
                result = getattr(self, generate)(spec)
            else:
                raise Exception(f"Invalid specification: {name}")
        except:
            logger.exception(
                f"[{name}] generation failed", extra={"transform": self.name}
            )
            raise

        # then, use the specified strategy to detect anomalies
        strategy = config.get("strategy")
        if strategy == None:
            # We are doing the default anomaly detection which is deviation from mean
            data, l_msg = self.process_spec_default(result, spec)
        elif strategy == "custom":
            # Custom callback
            data, l_msg  = self.process_spec_custom(result, spec)
        elif strategy not in valid_detection_strategies:
            raise Exception(f"{strategy} is not a valid detection strategy")
        else:
            # for now, we fallback to the default strategy
            data, l_msg  = self.process_spec_default(result, spec)
        msg += l_msg

        # The spec processor can return multiple dataframes
        if isinstance(data, pd.DataFrame):
            data = {name: data, "stats": {}}

        logger.debug(
            f"Processed anomalies",
            extra={"transform": self.name, "data": msg}
        )

        return data

    def process_spec_custom(self, datasets, profile, spec):
        msg = ""

        name = spec["name"]
        handlers = self.get_handlers(profile)

        # Custom...
        generate = spec["generate"]
        callback = None
        if (generate in handlers) and (not callable(handlers[generate])):
            callback = handlers[generate]
        elif hasattr(self, generate):
            callback = getattr(self, generate)

        if callback is None:
            raise Exception(f"[{name}] Invalid callback: {generate}")

        # Get hold of the data first...
        sources = self.get_spec_sources(spec, datasets)

        return callback(sources, spec), msg

    def process_spec_default(self, data, spec):
        """
        Handle one specification at a time..
        """

        msg = ""
        msg += f"Using default centroid distance anomaly detector" + "\n"

        config = spec["config"]
        msg += f"Config: {json.dumps(config, indent=4)}" + "\n"

        # Get hold of the data first...
        name = spec["name"]
        df = data[name]
        total_samples = len(df)

        dimensions = config.get("dimensions", df.columns)
        outputs = config.get("outputs", [])
        pkeys = config.get("primarykey", [])
        columns = list(set(dimensions + outputs + pkeys))
        df = df[columns]
        msg += f"Combined set of columns: {columns}" + "\n"

        # default anomaly detection
        tolerances = {
            "low": 1,
            "medium": 2,
            "high": 3,
        }

        tolerance = config.get("tolerance", "medium")
        scalefactor = tolerances.get(tolerance, 2)

        msg += f"(tolerance, scalefactor): ({tolerance}, {scalefactor})" + "\n"

        points      = df[dimensions].to_numpy()    # all data as an MxN matrix
        centroid    = np.mean(points, axis=0)   # the computed centroid of the dataset
        distances   = distance.cdist(points, np.array([centroid]), 'euclidean') # distances of each point to centroid
        stddev      = np.std(distances)         # std dev of distances
        threshold   = stddev*scalefactor
        anomalies   = np.where(distances.flatten()>threshold, 'anomaly', 'normal')    # flag where anomalies occur

        # add the anomaly label column
        label = name.replace(' ', '').replace('-', '')
        label = f"__is_anomaly__"
        df[label] = pd.Series(anomalies)

        # sample the normal data if needed
        normal_samples = config.get("normal_samples", "partial")
        partialsamplerate = 0.05
        samplerate_lut = {
            "all": 1.0,
            "partial": partialsamplerate,
            "none": 0.0
        }
        samplerate = samplerate_lut[normal_samples]

        df_a = df[df[label]=='anomaly']
        n_anomalies   = len(df_a)

        df_n = df[df[label]=='normal'].sample(frac=samplerate)
        df_n = df_n[0:min(3*n_anomalies,len(df_n))] # min 3x n_anomalies or 5% of normal samples
        n_nsamples    = len(df_n)

        df = pd.concat([df_a, df_n])


        # add a column indicating reason for anomaly
        def anomaly_note(row, threshold):
            metric = row["__anomaly_metric__"]
            if metric > threshold:
                return f"{round(metric/threshold,2)}x outside expected sample deviation"
            return f"within expected sample deviation"

        df["__anomaly_metric__"] = pd.Series(distances.flatten())
        df["__anomay_note__"] = df.apply(lambda x: anomaly_note(x, threshold), axis=1)

        # order the columns, make sure no duplicates
        cols = pkeys
        cols += [c for c in df.columns if "__" in c]
        cols += [c for c in dimensions if c not in cols]
        cols += [c for c in outputs if c not in cols]
        df = df[cols]

        perc = round(n_anomalies/total_samples*100, 2)
        msg += f"Anomalies: {n_anomalies}/{total_samples}={perc}%" + "\n"
        msg += f"Final columns: {cols}" + "\n"

        window, start_date, end_date = self.get_window_dates(config, self.args)

        # compute stats of interest
        stats = {
            "timestamp": f"{datetime.now().isoformat()}",
            "policy": config,
            "data_start_date": f"{start_date}",
            "data_end_date": f"{end_date}",
            "strategy": "centroid",
            "tolerance": tolerance,
            "n_rows": total_samples,
            "n_anomalies": n_anomalies,
            "perc_anomalies": perc,
            "normalsamples": normal_samples,
            "n_normalsamples": n_nsamples,
            "scalefactor": scalefactor,
            "threshold": threshold,
        }

        msg += f"Stats: {json.dumps(stats, indent=4)}" + "\n"

        return {name: df, "stats": stats}, msg

    def read_db_source(self, source):

        # Get the SQLAlchemy URI
        uri = self.get_db_uri(source)

        # Get the query
        query = self.get_db_query(source)

        # Create the engine
        engine = create_engine(uri)

        # Run the query
        df = pd.read_sql_query(satext(query), con=engine)

        # Now the input load...
        lineage = {
            "type": "lineage",
            "transform": self.name,
            "dependencies": [
                {
                    "type": "database",
                    "nature": "input",
                    "objects": [self.get_printable_db_uri(uri)],
                },
            ],
        }

        self.update_frame(source, df, lineage)

        return df

    def read_s3_data(self, filename, params, **kwargs):

        # assume we have a resolved s3fs object
        s3 = self.args['s3']
        if s3.exists(filename):
            df = pd.read_csv(s3.open(filename),**params)
            return df

        return None

    def get_spec_sources(self, spec, datasets):

        name = spec["name"]

        if ("sources" not in spec) and ("source" not in spec):
            raise Exception(f"[{name}] Invalid specification. Missing dataset")

        sources = spec.get("sources", spec.get("source"))
        if isinstance(sources, str):
            sources = [sources]

        policy = spec.get("missing", "fail")
        for s in sources:
            if s not in datasets:
                if policy == "fail":
                    raise Exception(f"[{name}] Missing source: {s}")

        return {s: datasets[s] for s in sources if s in datasets}

    def update_frame(self, source, df, lineage=None):

        if isinstance(source, str):
            name = source
            description = ""
        else:
            name = source["name"]
            description = source.get("description", "")

        if self.state.has_frame(name):
            return

        params = self.get_column_params(name, df)
        if lineage is not None:
            if isinstance(lineage, dict):
                params.append(lineage)
            else:
                params.extend(lineage)

        detail = {
            "name": name,
            "df": df,
            "frametype": "pandas",
            "description": description,
            "params": params,
            "transform": self.name,
            "history": [],
        }

        self.state.update_frame(name, detail)

    def construct_dataset_list(self, anomalyspecs):
        if not hasattr(self, 'get_dataset_registry'):
            raise Exception(
                "get_datasets expects get_dataset_registry method"
            )

        # call the overloaded method to get the dataset registry
        registry = self.get_dataset_registry()

        # what are all the datasets in the spec
        spec_datasets = []
        for spec in anomalyspecs:
            dataset = spec.get('config', {}).get('dataset')
            if dataset == None:
                continue
            spec_datasets.append(dataset)

        # iterate to keep only the datasets in the spec
        datasets = {}
        for dataset in registry.datasets:
            name = dataset.name
            for subset in dataset.subsets:
                d = f"{name}-{subset['name']}"
                if d in spec_datasets:
                    # make a lookup table
                    datasets[d] = dataset

        return datasets

    def get_window_dates(self, config, args):
        # get the window size
        window = config.get("window")
        if window == None or window == "":
            window = "1"
        try:
            window = int(window)
        except:
            raise Exception(
                "window param in config needs to be a string integer"
            )

        # determine start and end dates for dataset
        end_date = args["run_date"]
        start_date = end_date + timedelta(days=-window+1)

        return window, start_date, end_date


    def get_dataset_s3(self, spec, datasets):
        """
        Use the dataset object to read the dataset
        """

        if not hasattr(self, "get_dataset"):
            raise Exception(
                "get_dataset_s3 expects get_dataset method"
            )

        name = spec["name"]
        config = spec["config"]
        window, start_date, end_date = self.get_window_dates(config, self.args)

        dataset = config["dataset"]
        pieces = dataset.split('-')
        dataset_main = "-".join(pieces[:-1])
        dataset_subset = pieces[-1]
        params = spec.get("params", {})

        filename = config.get("filename")
        if filename == None:
            raise Exception(
                "filename param in config not provided"
            )

        cache = self.args.get("cache", False)
        cachename = f"{dataset}-{start_date}-{end_date}"
        cachefile = f"cache/{self.name}-cache-" + cachename + ".csv"

        if cache:
            try:
                os.makedirs(os.path.dirname(cachefile))
            except:
                pass
            if os.path.exists(cachefile):
                logger.debug(
                    "Read cached {}".format(name), extra={"transform": self.name}
                )
                df = pd.read_csv(cachefile, **params)
                return {name: df}

        datasetobj = self.get_dataset(dataset_main)

        df, metadata = datasetobj.read_data(
            start_date,
            end_date,
            filename=filename,
            readfunc=self.read_s3_data,
            params=params,
        )

        logger.debug("Read {}".format(name), extra={"transform": self.name})

        # Cache it for future use...
        if cache:
            df.to_csv(cachefile, index=False)

        # Insert lineage if possible
        lineage = None
        if ("files" in metadata) and (len(metadata["files"]) > 0):
            lineage = {
                "type": "lineage",
                "transform": self.name,
                "dependencies": [
                    {
                        "type": "file",
                        "nature": "input",
                        "objects": [metadata["files"][-1]],
                    },
                ],
            }

        self.update_frame(spec, df, lineage)

        return {name: df}

    def get_identifier(self, spec):

        identifier  = f"{spec['id']}-{spec['name']}"
        identifier = re.sub(r'\W+', '_', identifier)
        return identifier

    def s3_store_result(self, spec, data):

        id          = spec['id']
        name        = spec['name']
        identifier  = self.get_identifier(spec)
        run_date    = self.args['run_date']
        s3          = self.args['s3']
        epoch       = time.time()

        config      = spec["config"]

        # get the dataframe and
        # add additional columns
        df = data[name]
        df["__run_date__"] = run_date

        dimensions  = config.get('dimensions', df.columns)

        # get the stats object
        stats = data["stats"]

        # where are we storing it?
        anomaliesfile   = os.path.join(self.args['s3root'], f"{identifier}/{run_date}/{epoch}__outliers.csv")
        statsfile       = os.path.join(self.args['s3root'], f"{identifier}/{run_date}/{epoch}__stats.json")
        plotfile_1dim   = os.path.join(self.args['s3root'], f"{identifier}/{run_date}/{epoch}__plot_1dim.png")
        plotfile_ndim   = os.path.join(self.args['s3root'], f"{identifier}/{run_date}/{epoch}__plot_ndim.png")

        # plot the results
        plot = pd.plotting.parallel_coordinates(df,
                                                class_column='__is_anomaly__',
                                                cols=dimensions,
                                                colormap=plt.get_cmap("Set1"))
        plt.title('Outlier Mapping by Dimension')
        # plt.savefig("/Users/achintthomas/Desktop/test_ndim.png")        # plots
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        with s3.open(plotfile_ndim, 'wb') as fd:
            fd.write(img_data.getbuffer())
        plt.clf()

        df_plot = df[['__is_anomaly__', '__anomaly_metric__']]
        df_plot['y'] = 0 # for the y-axis
        plot = sns.scatterplot(data=df_plot, x="__anomaly_metric__", y="y",
                                hue="__is_anomaly__",
                                style="__is_anomaly__")
        plt.axvline(x=stats['threshold'],
                    ymin=0.3, ymax=0.7,
                    color='k', linestyle='--')
        plt.annotate('threshold',
                        xy=(stats['threshold'], 0.025))
        plt.title('Outlier Distance from Expected Sample Deviation')
        #plt.savefig("/Users/achintthomas/Desktop/test_1dim.png")
        img_data = io.BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        with s3.open(plotfile_1dim, 'wb') as fd:
            fd.write(img_data.getbuffer())
        plt.clf()

        # write to s3
        # anomalies
        with s3.open(anomaliesfile, 'w') as fd:
            df.to_csv(fd, index=False)

        # stats
        with s3.open(statsfile, 'w') as fd:
            json.dump(stats, fd)

        msg = note(df, f"{name} - Anomalies Tagged") + "\n"
        msg += f"s3 location: {anomaliesfile}" + "\n"

        logger.debug("Wrote anomalies".format(name),
                        extra={"transform": self.name,
                                "data": msg})

    def store_result(self, spec, data):

        logger.debug("Using default store: s3",
                     extra={
                         'transform': self.name
                     })

        # Now store in s3
        return self.s3_store_result(spec, data)

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "Start execution", extra=self.config.get_extra({"transform": self.name})
        )

        # Will be used in other places..
        self.state = state

        # Get the anomaly profile
        profile = self.get_profile()

        # Get specs from anomaly profile
        specs = self.get_specs(profile)

        # get the dataset lookup table
        datasets = self.construct_dataset_list(specs)

        # Now go through each spec and generate anomaly reports
        for spec in specs:
            enable = spec.get("enable", True)
            if not enable:
                continue

            # process the spec to detect outliers
            try:
                data = self.process_spec(spec, datasets)

                # write the detected outliers
                self.store_result(spec, data)
            except:
                logger.exception(f"Failed: {spec['name']}",
                                 extra={
                                     'transform': self.name
                                 })

        # Done
        logger.debug(
            "Complete execution", extra=self.config.get_extra({"transform": self.name})
        )

        ###########################################
        # => Return
        ###########################################
        return state

    def validate_results(self, what, state):
        pass
