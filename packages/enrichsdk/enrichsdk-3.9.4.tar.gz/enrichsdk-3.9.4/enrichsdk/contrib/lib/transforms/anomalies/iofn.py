import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
import json

def call_api(url, args):
    msg = ""
    server = args['apiurl']
    apikey = args['apicred']['api_key']
    htuser = args.get('htaccess', {}).get('user', "")
    htpass = args.get('htaccess', {}).get('pass', "")

    headers = {
        'accept': 'application/json',
        'X-API-Key': apikey,
    }

    msg += f"Calling URL: {url}" + "\n"
    if (htuser == '') and (htpass == ''):
        response = requests.get(url,
                            headers=headers,
                                verify=False,
                                timeout=10)
    else:
        response = requests.get(url,
                                headers=headers,
                                auth=HTTPBasicAuth(htuser, htpass),
                                verify=False,
                                timeout=10)
    is_valid = True if response.status_code == 200 else False
    msg += f"Response: {response.reason}" + "\n"

    return is_valid, response, msg


def load_profile_api(args):
    msg = ""

    # ## -- TO-DO --
    # ## remove this once the API is ready
    # anomalyspec = {
    #     "specs": [
    #         {
    #             "schema": "OutlierPolicy",
    #             "id": 4,
    #             "name": "scribbledata",
    #             "desc": "Service Number",
    #             "notes": "SSSS",
    #             "tags": "",
    #             "active": true,
    #             "created_at": "2022-05-11T11:12:09.243513+00:00",
    #             "created_by": "superman",
    #             "modified_at": "2022-05-11T11:12:09.243600+00:00",
    #             "modified_by": "superman",
    #             "config": {
    #                 "dataset": "mtn",
    #                 "filename": "data.csv",
    #                 "window": "7",
    #                 "columns": [],
    #                 "strategy": "centroid",
    #                 "tolerance": "high"
    #             }
    #         }
    #     ]
    # }
    # return anomalyspec, True, "Short circuit till API is ready\n"
    # ## -- END TO-DO --

    # API endpoint for anomalies service
    apiserver = args['apiserver'] if "https://" in args['apiserver'] else f"https://{args['apiserver']}"
    args['apiurl'] = f"{apiserver}/api/v2"

    # first, get the specs to identify what anomaly apps exist
    url = f"{args['apiurl']}/dashboard/apps/"
    is_valid, response, l_msg = call_api(url, args)
    msg += l_msg
    if not is_valid:
        return None, is_valid, msg

    # now, loop through to get the anomaly app name
    app_name = None
    jdata = response.json()['data']
    for app_id, app_spec in jdata.items():
        if app_spec['category'] == 'outliers':
            app_name = app_spec['spec']['name']
            break
    if app_name == None:
        msg += f"No outlier apps found, cannot proceed" + "\n"
        return None, False, msg

    # now, get the anomaly specs from the app
    url = f"{args['apiurl']}/app/outliers/{urllib.parse.quote(app_name)}/policies"
    is_valid, response, l_msg = call_api(url, args)
    msg += l_msg
    if not is_valid:
        return None, is_valid, msg

    # now, loop through to get the anomaly specs
    jdata = response.json()['data']
    msg += f"Found {len(jdata)} anomaly specs" + "\n"
    anomalyspec = {
        "specs": jdata
    }

    return anomalyspec, is_valid, msg
