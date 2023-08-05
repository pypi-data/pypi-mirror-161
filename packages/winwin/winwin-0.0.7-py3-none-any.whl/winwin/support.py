# -*- coding: utf-8 -*-
# @Time    : 2022-07-10 09:42
# @Author  : zbmain
"""
support: 工具
├── 环境配置.env:   文件目录 > 跟目录 > Home环境目录[~.winwin_hub]
├── mysql connect
├── odps connect
├── holo connect
├── redis connect
├── oss bucket
├── openseach conf
└── 一些常用功能函数
"""
import csv
import logging
import os
from urllib.parse import urlparse, parse_qs

from dotenv import load_dotenv

try:
    import env
except ModuleNotFoundError as e:
    from . import env

logging.info("hub_home path:[%s]" % env.HUB_HOME)

# 项目.跟目录
CURRENT_DIR = os.path.join(os.path.abspath('.'), '')
# 项目.跟目录创建.cache
CACHE_DIR = os.path.join(CURRENT_DIR, '.cache')
if not os.path.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)


def get_exists_file(file: str):
    """查找目录优先级: support.py目录 > project跟目录 > HOME环境目录(~.winwin_hub)"""
    dirs = [os.path.dirname(os.path.abspath(__file__)), os.path.abspath('.'),
            os.path.join(os.path.expanduser('~'), '.winwin_hub')]
    for _dir in dirs:
        filepath = os.path.join(_dir, file)
        if os.path.exists(filepath):
            return filepath


# 文件目录、项目跟目录、HOME环境目录, 加载.env环境文件
env_file = get_exists_file('.env')
env_file and load_dotenv(env_file)
logging.info("current env file used path:[%s]" % env_file)


# MYSQL
def parse_mysql_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'user': parsed_uri.username,
        'password': parsed_uri.password,
        'port': parsed_uri.port,
        'database': parsed_uri.path[1:],
        'charset': 'utf8mb4' if query.get('charset') is None else query['charset'][0]
    }


def mysql_connect(name="MYSQL_URI"):
    """MYSQL Connect"""
    import pymysql
    return pymysql.connect(**parse_mysql_uri(os.environ[name]), autocommit=True, cursorclass=pymysql.cursors.DictCursor)


# OSS
def parse_oss_uri(uri):
    parsed_uri = urlparse(uri)
    return {
        'endpoint': '{}://{}'.format(parsed_uri.scheme, parsed_uri.hostname),
        'access_key_id': parsed_uri.username,
        'access_key_secret': parsed_uri.password,
        'bucket': parsed_uri.path[1:],
    }


def oss_connect(name="OSS_URI"):
    """OSS Bucket"""
    import oss2
    config = parse_oss_uri(os.environ[name])
    return oss2.Bucket(oss2.Auth(config['access_key_id'], config['access_key_secret']), config['endpoint'],
                       config['bucket'])


def oss_get_object_cache(url, bucket=None):
    """下载 OSS文件到缓存目录"""
    bucket = bucket or oss_connect()
    cache_file = os.path.join(CACHE_DIR, os.path.basename(url))
    if not os.path.isfile(cache_file) or os.path.getsize(cache_file) == 0:
        parsed = urlparse(url)
        bucket.get_object_to_file(parsed.path[1:], cache_file)
    return cache_file


def oss_get_object_topath(url, save_path='./', bucket=None):
    """下载 OSS文件到指定目录"""
    bucket = bucket or oss_connect()
    save_path = not os.path.basename(save_path) and (os.path.join(save_path, os.path.basename(url))) or save_path
    if not os.path.isfile(save_path) or os.path.getsize(save_path) == 0:
        parsed = urlparse(url)
        bucket.get_object_to_file(parsed.path[1:], save_path)
    return save_path


def oss_get_object_stream(url, bucket=None):
    """下载 OSS文件流"""
    bucket = bucket or oss_connect()
    oss_url = urlparse(url).path[1:]
    return bucket.get_object(oss_url).read()


def oss_upload_object(file_url, oss_url, bucket=None):
    """上传 本地文件到OSS"""
    bucket = bucket or oss_connect()
    file_name = os.path.basename(file_url)
    oss_url = urlparse(oss_url).path[1:]
    oss_url = not os.path.basename(oss_url) and (os.path.join(oss_url, file_name)) or oss_url
    bucket.put_object_from_file(oss_url, file_url)
    return '%s%s/%s' % ('oss://', bucket.bucket_name, oss_url)


# ODPS
ODPS_TUNNEL, ODPS_LIMIT = True, False


def parse_odps_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    ODPS_TUNNEL = True if query.get('tunnel') is None else query.get('tunnel')[0]
    ODPS_LIMIT = False if query.get('limit') is None else query.get('limit')[0]
    return {
        'endpoint': '{}://{}'.format(parsed_uri.scheme, os.path.join(parsed_uri.hostname, parsed_uri.path[1:])),
        'access_id': parsed_uri.username,
        'secret_access_key': parsed_uri.password,
        'project': query.get('project') and query.get('project')[0] or 'zhidou_hz'
    }


def odps_connect(name="ODPS_URI"):
    """ODPS / Maxcompute Connect"""
    from odps import ODPS
    return ODPS(**parse_odps_uri(os.environ[name]))


def odps_download_with_sql(sql, save_path, connect=None, sep=','):
    """通过SQL下载全量数据"""
    connect = connect or odps_connect()
    save_path = os.path.join(CURRENT_DIR, save_path)
    if sql.endswith('.sql'):
        with open(os.path.join(CURRENT_DIR, sql), 'r') as f:
            fsql = f.read()
    else:
        fsql = sql
    with connect.execute_sql(fsql).open_reader(tunnel=ODPS_TUNNEL, limit=ODPS_LIMIT) as reader:
        headers = reader.schema.names
        with open(save_path, 'w', encoding='utf8') as writefile:
            csv_writer = csv.writer(writefile, delimiter=sep)
            csv_writer.writerow(headers)
            for record in reader:
                csv_writer.writerow(dict(record).values())


# OpenSearch
def parse_ops_uri(uri):
    '''
    security_token有值,type=sts;
    security_token无值,type=access_key;
    '''
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    security_token = query.get('security_token') and query.get('security_token')[0]
    assert query.get('app_name'), """opensearch-uri have to set 'app_name'"""
    return {
        'protocol': parsed_uri.scheme,
        'endpoint': parsed_uri.hostname,
        'access_key_id': parsed_uri.username,
        'access_key_secret': parsed_uri.password,
        'type': security_token and 'sts' or 'access_key',
        'security_token': security_token,
        'app_name': query.get('app_name') and query.get('app_name')[0] or ''
    }


def ops_conf(name="OPS_URI"):
    """OpenSearch Conf"""
    return parse_ops_uri(os.environ[name])


# Hologres
def parse_holo_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'user': parsed_uri.username,
        'password': parsed_uri.password,
        'port': parsed_uri.port,
        'dbname': query.get('dbname') and query.get('dbname')[0] or 'zhidou_hz'
    }


def holo_connect(name="HOLO_URI"):
    """Holo Connect"""
    import psycopg2
    return psycopg2.connect(**parse_holo_uri(os.environ[name]))


# Redis
def parse_redis_uri(uri):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    return {
        'host': parsed_uri.hostname,
        'username': parsed_uri.username,
        'password': parsed_uri.password,
        'port': parsed_uri.port,
        'db': query.get('db') and int(query.get('db')[0]) or 0,
        'decode_responses': query.get('decode_responses') and bool(query.get('decode_responses')[0]) or False
    }


redis_pool = None


def redis_connect(name="REDIS_URI"):
    """Redis Connect"""
    import redis
    global redis_pool
    redis_uri = parse_redis_uri(os.environ['REDIS_URI'])
    if not (redis_pool and redis_pool.connection_kwargs['host'] == redis_uri['host'] \
            and redis_pool.connection_kwargs['db'] == redis_uri['db']):
        redis_pool = redis.ConnectionPool(**redis_uri)
    return redis.StrictRedis(connection_pool=redis_pool)


def parse_nebula_uri(uri=None):
    parsed_uri = urlparse(uri)
    query = parse_qs(parsed_uri.query)
    servers = [(parsed_uri.hostname, parsed_uri.port)] + [(server.split(':')[0], int(server.split(':')[1])) for server
                                                          in query.get('server', [])]
    return {
        'servers': servers,
        'username': parsed_uri.username,
        'password': parsed_uri.password,
        'space': query.get('space') and query.get('space')[0] or '',
        'comment': query.get('comment') and query.get('comment')[0] or '',
        'heart_beat': query.get('heart_beat') and int(query.get('heart_beat')[0]) or 10,
    }


nebula_pool = None


def nebula_connect(name='NEBULA_URI'):
    uri = parse_nebula_uri(os.environ[name])
    from nebula3.gclient.net import ConnectionPool
    from nebula3.Config import Config
    global nebula_pool
    if not nebula_pool:
        nebula_pool = ConnectionPool()
        nebula_pool.init(uri['servers'], Config())
    session = nebula_pool.get_session(uri['username'], uri['password'])
    session.space, session.comment, session.heart_beat = uri['space'], uri['comment'], uri['heart_beat']
    return session
