import os
import json
from ...utils.logger import Logger
logger = Logger()


def prepare_sql_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index:
            sql_data = {
                'query': args[index],
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
            return sql_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_sql_data failed with error : ' + str(e))
    return {}


def prepare_mysql_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index:
            query = args[index]
            if len(args) > index+1:
                values = args[index+1]
                if isinstance(values, dict):
                    for key, value in values.items():
                        query = query.replace("%({0})s".format(key), value)
                if isinstance(values, (list, tuple)):
                    for value in values:
                        query = query.replace("%s", value, 1)

            sql_data = {
                'query': query,
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
            return sql_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_mysql_data failed with error : ' + str(e))
    return {}


def prepare_mongo_query_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index:
            query = json.dumps(args[index])
            query = query.replace("None", "null")
            sql_data = {
                'query': query,
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
            return sql_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_mongo_query_data failed with error : ' + str(e))
    return {}


def prepare_multiple_mongo_query_data(data):
    try:
        sql_data = prepare_mongo_query_data(data)
        args = data.get('args', [])
        index = data['config']['argsIndex'] + 1
        if len(args) > index:
            query = json.dumps(args[index])
            query = query.replace("None", "null")
            sql_data['query'] += query

        return sql_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_mongo_query_data failed with error : ' + str(e))
    return {}


def prepare_lfi_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index + 1:
            lfi_data = {
                'mode': 'write' if 'w' in args[index + 1] else 'read',
                'path': args[index],
                'realpath': os.path.realpath(args[index]),
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
            return lfi_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_lfi_data failed with error : ' + str(e))
    return {}


def prepare_shellShock_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index:
            shellShock_data = {
                'command': args[index],
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
            return shellShock_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_shellShock_data failed with error : ' + str(e))
    return {}


def prepare_SSRF_data(data):
    try:
        args = data.get('args', [])
        index = data['config']['argsIndex']
        if len(args) > index + 1:
            return {
                'url': args[index + 1],
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
        if len(args) > index:
            return {
                'url': args[index],
                'poSessionId': data.get('result', {}).get('poSessionId', '')
            }
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_SSRF_data failed with error : ' + str(e))
    return {}


def prepare_dynamodb_data(data):
    try:
        if len(data.get('args', [])) > 0:
            dynamodb_data = {
                "dynamoDbParams": data['args'],
                'poSessionId': data['result']['poSessionId']
            }
            return dynamodb_data

        if len(data.get('kwargs', {})) > 0:
            dynamodb_data = {
                "dynamoDbParams": data['kwargs'],
                'poSessionId': data['result']['poSessionId']
            }
            return dynamodb_data

        dynamodb_data = {
            "dynamoDbParams": {},
            'poSessionId': data['result']['poSessionId']
        }
        return dynamodb_data
    except Exception as e:
        logger.info() and logger.write(
            'rasp.prepare_dynamodb_data failed with error : ' + str(e))
    return {}
