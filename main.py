"""
Facebook organic extractor

Represents insights for Facebook Pages and Page posts.
API documentation: https://developers.facebook.com/docs/graph-api/reference/insights/

Author:
    Raccoon.Monks
"""



import requests
import logging as log
import os
from datetime import datetime, timedelta
import pytz
import time
from google.cloud import bigquery
from google.cloud import secretmanager
import json
from utils import *





def config_log():
    """
    Configure logging level, output format and sends it to a file.
    """

    today = datetime.today().strftime("%Y%m%d")
    logging_level = 20
    # log_filename = f'logs/instagram_organic_{today}.log'
    log.basicConfig(
        # filename=log_filename,
        level=logging_level,
        format=f'[%(asctime)s.%(msecs)03d] %(levelname)s: %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True)


def get_token(config):
    """
    Get token from file to authenticate API calls.

    Arguments:
        config {dict} -- params with the path to token file

    Returns:
        {str} -- authentication token
    
    """
    client = secretmanager.SecretManagerServiceClient()
    request = {
        "name": f"projects/{SECRET_PROJECT_ID}/secrets/{FACEBOOK_CREDENTIALS_NAME}/versions/latest"
    }
    response = client.access_secret_version(request)
    secret_string = response.payload.data.decode("UTF-8")
    credentials = json.loads(secret_string)
    
    
    return credentials["access_token"]



def make_api_call(endpoint, params, retry=False):
    """
    Make an API call and check for errors.
    Exits if an unexpected error occur.

    Arguments:
        endpoint {str} -- the URL to be called
        params {dict} -- params

    Returns:
        json_response {dict} -- the response of the call
    """

    response = requests.get(
        endpoint,
        params=params
    )

    json_response = response.json()
    if response.status_code == 200:
        return json_response

    if response.status_code == 500:
        if not retry:
            log.warning("Server error. Retrying in 5 minutes")
            time.sleep(300)
            make_api_call(endpoint, params, retry=True)
        else:
            log.error(response.text)
            raise Exception("API call failed")

    # error when media was posted before account was converted to business
    if json_response["error"].get("code") == 100 and\
       json_response["error"].get("error_subcode") == 2108006:
        return "continue"

    log.error(response.text)
    raise Exception("API call failed")


def get_account_general_data(token, account_id):
    """
    Get User account data.
    https://developers.facebook.com/docs/graph-api/reference/page/

    Arguments:
        token {str} -- authentication token
        account_id {str} -- id of the account

    Returns:
        json_response {dict} -- API response with account fields
    """

    log.info("Retrieving account basic data")

    account_data_url = ACCOUNT_GENERAL_DATA_ENDPOINT.format(account_id)

    params = {
        "access_token": token,
        "fields": ",".join(ACCOUNT_FIELDS) + ",ratings"
    }

    json_response = make_api_call(account_data_url, params)
    json_response["ratings"] = json_response.get("ratings").get("data")


    return json_response


def get_account_insights(token, account_id):
    """
    Get User account insights with daily and lifetime metrics.
    For daily metrics, get data from the past day.
    https://developers.facebook.com/docs/graph-api/reference/v14.0/insights

    Arguments:
        token {str} -- authentication token
        account_id {str} -- id of the account

    Returns:
        account_insights {list} -- list with all metrics
    """

    log.info("Retrieving account insights")

    account_insights_url = ACCOUNT_INSIGHTS_ENDPOINT.format(account_id)
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago = (today - timedelta(days=2)).strftime("%Y-%m-%d")

    params = {
        "access_token": token,
        "until": today.strftime("%Y-%m-%d")
    }

    account_insights = []
    period = "day"
    
    log.info(f"get account insights for period {period}")
    metrics = ",".join(ACCOUNT_METRICS[period])

    params["metric"] = metrics
    params["period"] = period
    params["since"] = two_days_ago
 

    json_response = make_api_call(account_insights_url, params)

    account_insights.append(json_response)

    return account_insights


def get_account_media_ids(token, account_id):
    """
    Get all post ids from a user.
    https://developers.facebook.com/docs/graph-api/reference/page-post/

    Arguments:
        token {str} -- authentication token
        account_id {str} -- id of the account

    Returns:
        media_ids {list} -- all media ids
    """

    log.info("Retrieving posts ids")

    media_url = MEDIA_ID_ENDPOINT.format(account_id)
    params = {
        "access_token": token,
        "fields": "account_id, created_time",
        "limit": 100
    }

    next_media_page = ""
    media_ids = []

    today = datetime.now(tz=pytz.utc)
    d31_ago = today - timedelta(days=120)
    breaking = False

    while next_media_page is not None and breaking is False:
        json_response = make_api_call(media_url, params)
        media_ids += json_response.get("data")
        for keys in  media_ids:
            row = dict(keys)
            max_date = datetime.strptime(
                    row['created_time'],
                    "%Y-%m-%dT%H:%M:%S%z")
        if max_date < d31_ago:
            breaking=True
        else:
            next_media_page = json_response.get("paging").get("next")
            params["after"] = json_response\
                .get("paging")\
                .get("cursors")\
                .get("after")

    return media_ids




def get_media_general_data(token, media_ids):
    """
    Get basic data for all posts.
    https://developers.facebook.com/docs/graph-api/reference/page-post/

    Arguments:
        token {str} -- authentication token
        media_ids {list} -- all media ids

    Returns:
        media_data_last_31d {list} -- media data that was created up to 31 days ago,
            each media fields is a dict
    """

    log.info("Retrieving media basic data")

    fields = ",".join(MEDIA_FIELDS)
    params = {
        "access_token": token,
        "fields": fields
    }

    media_data = []
    start_time = time.time()
    for media_id in media_ids:
        if time.time() - start_time > 500:
            break
        else:
            media_url_id = MEDIA_GENERAL_DATA_ENDPOINT.format(media_id["id"])
            json_response = make_api_call(media_url_id, params)
            media_data.append(json_response)        
    media_data_last_31d = media_data

    return media_data_last_31d


def get_media_insights(token, media_data):
    """
    Get insights for all media, according to media type.
    https://developers.facebook.com/docs/graph-api/reference/insights/#page-posts

    Arguments:
        token {str} -- authentication token
        media_data {list} -- all media data, each media fields is a dict

    Returns:
        media_insights {list} -- all media insights, each media insight is a dict
    """

    log.info("Retrieving post insights")
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago = (today - timedelta(days=2)).strftime("%Y-%m-%d")
    params = {
            "access_token": token}
    media_insights = []
    log.info(f"get insights for each post: period lifetime")
    for media in media_data:
        media_id = media["id"]
        
        insights_url_id = MEDIA_INSIGHTS_ENDPOINT.format(media_id)


        metrics = ",".join(MEDIA_METRICS)
        
        params["metric"] = metrics
        params["period"] = "lifetime"


        json_response = make_api_call(insights_url_id, params)
        media_insights.append(json_response)
            

    return media_insights


def transform_account_daily_data(account_data, account_insights):
    """
    Transforms and joins account daily data and insights,
    according to BigQuery needs.

    Arguments:
        account_data {dict} -- account basic fields
        account_insights {list} -- all account metrics

    Returns:
        account_daily_data {dict} -- account fields and metrics by date
    """

    log.info("Transforming account daily data")

    account_daily_data = {}
    for metric in account_insights[0]["data"]:
        if metric["name"] == "follower_count":
            continue
        else:
            for value in metric["values"]:
                day = value["end_time"].split("T")[0]
                account_daily_data[day] = []
                new_row = {}
                new_row["account_id"] = account_data["id"]
                new_row["username"] = account_data["username"]
                account_daily_data[day].append(new_row)
            break

    for metric in account_insights[0]["data"]:
        metric_name = metric["name"]
        for value in metric["values"]:
            day = value["end_time"].split("T")[0]
            metric_value = value["value"]

            account_daily_data[day][0][metric_name] = metric_value

    return account_daily_data


def transform_account_lifetime_data(account_data, account_insights):
    """
    Transforms and joins account lifetime data and insights,
    according to BigQuery needs.

    Arguments:
        account_data {dict} -- account basic fields
        account_insights {list} -- all account metrics

    Returns:
        account_lifetime_data {dict} -- account fields and metrics
    """

    log.info("Transforming account lifetime data")

    account_lifetime_data = {}

    account_lifetime_data.update(account_data)
    account_lifetime_data["account_id"] = account_data["id"]
    del account_lifetime_data["id"]

    return account_lifetime_data


def transform_account_data(account_data, account_insights):
    """
    Transforms and joins account lifetime and daily data and insights,
    according to BigQuery needs.

    Arguments:
        account_data {dict} -- account basic fields
        account_insights {list} -- all account metrics

    Returns:
        transformed_account_data {dict} -- account data, by lifetime and daily metrics
    """

    transformed_account_data = {}

    daily_data = transform_account_daily_data(
        account_data,
        account_insights)
    transformed_account_data["daily"] = daily_data

    lifetime_data = transform_account_lifetime_data(
        account_data,
        account_insights)
    transformed_account_data["lifetime"] = [lifetime_data]

    return transformed_account_data


def transform_media_data(account_id, media_data, media_insights):
    """
    Transforms and joins posts data and insights,
    according to BigQuery needs.
    Separetes into story and post (image, video and carousel) data.

    Arguments:
        account_id {str} -- id of the account
        media_data {list} -- all posts data, each posts fields is a dict
        media_insights {list} -- all posts insights, each posts insight is a dict

    Returns:
        transformed_media_data {dict} -- account data, by lifetime and daily metrics
    """


    log.info("Transforming media data")

    transformed_media_data = {}
    transformed_media_insights = {}
    for media in media_insights:

        media_id = media["data"][0]["id"].split("/")[0]
        transformed_media_insights[media_id] = {}
        for metric in media["data"]:
            metric_name = metric["name"]
            metric_value = metric["values"][0]["value"]
            transformed_media_insights[media_id][metric_name] = metric_value
            
            

    post_data = []
    for media in media_data:
        if transformed_media_insights.get(media["id"]) is None:
            continue
        insights = transformed_media_insights[media["id"]]
        media.update(insights)
        media["created_date"] = datetime.strptime(
                media["created_time"], 
                '%Y-%m-%dT%H:%M:%S+%f')\
                .strftime("%Y-%m-%d %H:%M:%S %Z")
        del media["created_time"]
        post_data.append(media)

    transformed_media_data["post"] = post_data

    return transformed_media_data



def get_schema(table_type):
    """
    Get schema for BigQuery table from json file, according to type.
    Possible types: daily, lifetime and  post
    
    Arguments:
        table_type {str} -- type of table

    Returns:
        {dict} -- BigQuery table schema
    """

    with open(SCHEMA_FILENAME, "r") as schema_file:
        schemas = json.load(schema_file)

    return schemas[table_type]

get_schema("daily")

def bigquery_save_data(config, table_name, data, schema):
    """
    Load json data to BigQuery table.

    Arguments:
        config {dict} -- configuration with BigQuery params
        table_name {str} -- name of the table that will receive data
        data {list} -- json data to be loaded
        schema {dict} -- BigQuery table schema
    """

    log.info(f"Loading data to {table_name}")

    bigquery_client = bigquery.Client(config["project_id"])
    dataset = bigquery_client.dataset(config["dataset_id"])
    table_ref = dataset.table(table_name)

    job_config = bigquery.LoadJobConfig()
    job_config.create_disposition = "CREATE_IF_NEEDED"
    job_config.time_partitioning = bigquery.table.TimePartitioning()
    job_config.schema = schema
    job_config.write_disposition = "WRITE_TRUNCATE"

    job = bigquery_client.load_table_from_json(
        data,
        table_ref,
        job_config=job_config
    )

    try:
        job.result()
    except Exception:
        log.error(job.errors)


def save_data(config, account_data, media_data):
    """
    Save all data to BigQuery tables.

    Arguments:
        config {dict} -- configuration with BigQuery params
        account_data {dict} -- lifetime and daily data
        media_data {dict} -- posts data
    """

    username = account_data["lifetime"][0]["username"]
    today = datetime.today()
    yesterday = (today - timedelta(days=1)).strftime("%Y%m%d")

    for table, data in account_data.items():
        schema = get_schema(table)
        if table == "daily":
            for day, rows in data.items():
                partition = day.replace("-", "")
                table_name = "facebook_account_" + table + "_" + username
                table_name += "$" + partition
                bigquery_save_data(config, table_name, rows, schema)
        else:
            table_name = "facebook_account_" + table + "_" + username
            table_name += "$" + yesterday
            bigquery_save_data(config, table_name, data, schema)
 
    for table, data in media_data.items():
        schema = get_schema(table)
        table_name = "facebook_" + table + "_" + username
        table_name += "$" + yesterday
        bigquery_save_data(config, table_name, data, schema)


def etl(config):
    """
    Get account and media data from instagram API,
    transform the data and load to BigQuery

    Arguments:
        config {dict} -- report configuration params
    """

    config_log()
    account_id = config["account_id"]
    token = get_token(config)

    try:
        log.info("Starting extraction")
        account_data = get_account_general_data(token, account_id)
        account_insights = get_account_insights(token, account_id)

        data = {}
        media_ids = get_account_media_ids(token, account_id)

        media_data = get_media_general_data(token, media_ids)
        media_insights = get_media_insights(token, media_data)

        transformed_account_data = transform_account_data(
            account_data,
            account_insights)

        transformed_media_data = transform_media_data(
            account_id,
            media_data,
            media_insights)

        data["account_data"] = transformed_account_data
        data["media_data"] = transformed_media_data
        save_data(config, transformed_account_data, transformed_media_data)
        log.info("End of extraction")
    except Exception as error:
        log.error(error)
        return 500, error
    
    return 200, data


def main(request):
    config = {
        "account_id": "",
        "project_id": "",
        "dataset_id": ""
    }
    status_code, data = etl(config)

    if status_code == 500:
      return (data, 500)
    return (data, 200)

