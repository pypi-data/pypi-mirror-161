"""
Module to facilitate access to Enrich Server API
and also show on the command line.

Visit <server>/api/v1.0/schema to understand the available
API calls.

"""

import json
import requests
import re
from collections import OrderedDict
from base64 import b64encode, b64decode

from .draw import *


class Backend:
    """
    Class to access Enrich Server API
    """

    def __init__(self, config):
        """
        Initialize an access object

        Args:

           config (dict): Should have 'server' and 'key'.
        """

        self.config = config
        assert "server" in config
        assert "key" in config
        assert "htpasswd_user" in config
        assert "htpasswd_pwd" in config

    def get_api_url(self, path, use_prefix=True):

        path = path.replace("//", "/")
        server = self.config["server"]

        # Avoid double lines...
        if server[-1] == "/":
            server = server[:-1]
        if ((len(path) > 0) and (path[0] == "/")):
            path = path[1:]

        if use_prefix:
            apiversion = self.config.get("version", "v2")
            url = "{}/api/{}/{}".format(server, apiversion, path)
        else:
            url = "{}/{}".format(server, path)

        return url

    def call(self, url, params={}, method="get", data={}):
        """
        Call backend with some extra query parameters

        Args:

           path (str): API path suffix (after api/v1.0/)
           params (dict): Query parameters
        """

        method = str(method).lower()

        key = self.config["key"]
        user = self.config['htpasswd_user']
        pwd = self.config['htpasswd_pwd']
        auth = b64encode(f"{user}:{pwd}".encode('utf-8')).decode('utf-8')

        headers = {
            "X-API-Key": key,
            "Authorization": f"Basic {auth}",
            "Accept": "application/json",
        }

        try:
            if method == "get":
                response = requests.get(
                    url,
                    verify=False,  # ignore SSL checks
                    headers=headers,
                    params=params,
                )
            elif method == "post":
                headers["Content-Type"] = "application/json"
                response = requests.post(
                    url, verify=False, headers=headers, params=params, json=data
                )
            else:
                raise Exception("Only get/post supported")

            if response.status_code not in [200, 400, 404]:
                return {
                    "status": "error",
                    "message": response.content[:100].decode("utf-8"),
                }
            return response.json(object_pairs_hook=OrderedDict)

        except requests.exceptions.ConnectionError as e:
            return {"status": "error", "message": "Connection refused"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def status(self, offset=0, page=20):
        """
        Shows a list of tasks/pipelines that ran/are running

        Args:
           offset (int): Offset in the execution list
           page (int): Page in the execution list
        """

        url = self.get_api_url("status")
        result = self.call(url, {"offset": offset, "page": page})

        return result

    def usecases(self):
        """
        Show all the usecases available on server
        """
        url = self.get_api_url("usecases")
        result = self.call(url)
        return result

    def health(self):
        url = self.get_api_url("")
        result = self.call(url)
        return result

    def pipelines(self, usecase):
        """
        Shows all pipelines within a given usecase

        Args:
           usecase (str): Name of the usecase
        """
        url = self.get_api_url("usecase/pipelines")
        result = self.call(url, {"usecase": usecase})
        return result

    def run_list(self, usecase, pipeline):
        """
        Shows all runs of a given pipeline

        Args:
           usecase (str): Name of the usecase
           pipeline (str): Name of the pipeline

        """
        url = self.get_api_url("dashboard/runs")
        result = self.call(url, {"usecasename": usecase, "pipelinename": pipeline})
        return result

    def run_detail(self, usecase, pipeline, runid):
        """
        Shows details of a given run of a pipeline

        Args:
           usecase (str): Name of the usecase
           pipeline (str): Name of the pipeline
           runid (str): Name of the run

        """
        url = self.get_api_url("usecase/pipeline/run/detail")
        result = self.call(
            url, {"usecase": usecase, "pipeline": pipeline, "runid": runid}
        )
        return result

    def tasks(self, usecase):
        """
        Shows all tasks within a given usecase

        Args:
           usecase (str): Name of the usecase
        """
        url = self.get_api_url("usecase/tasks")
        result = self.call(url, {"usecase": usecase})
        return result

    def task_run_list(self, usecase, task):
        """
        Shows all runs of a given task

        Args:
           usecase (str): Name of the usecase
           task (str): Name of the task
        """
        url = self.get_api_url("usecase/task/runs")
        result = self.call(url, {"usecase": usecase, "task": task})
        return result

    def task_run_detail(self, usecase, task, runid):
        """
        Shows details of a run

        Args:
           usecase (str): Name of the usecase
           task (str): Name of the task
           runid (str): Name of a run
        """
        url = self.get_api_url("usecase/task/run/detail")
        result = self.call(url, {"usecase": usecase, "task": task, "runid": runid})
        return result

    def scheduler_jobs_list(self):
        """
        List scheduler jobs
        """
        url = self.get_api_url("/scheduler/api/v1/jobs", use_prefix=False)
        result = self.call(url)
        return result

    def app_list(self):
        """
        List apps configured
        """
        url = self.get_api_url("dashboard/specs/")
        result = self.call(url)
        return result

    def app_detail(self, name):
        """
        Show details of an app
        """
        url = self.get_api_url(f"dashboard/specs/detail/{name}")
        result = self.call(url)
        return result


