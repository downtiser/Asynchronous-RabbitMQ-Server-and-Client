#Downtiser
''' The handler is used to dump data to the database or
load and update the data in database
'''
from RabbitMQ_async.RabbitMQ_async_server.conf import SETTINGS
import redis


def get_db_info():
    '''
    To get the current database information from
    settings.
    :return:
    '''
    db_info = {
        'db_path': SETTINGS.db_info['db_path'],
        'db_port': SETTINGS.db_info['db_port'],
        'db_password': SETTINGS.db_info['db_password'],
        'db_public_id': SETTINGS.db_info['db_public_id']
    }
    return db_info

def dump_task_info(host,task_id,res):
    '''
    To dump the task's result to the database and bind
    it with a task id.
    :param host:
    :param task_id:
    :param res:
    :return:
    '''
    db_info = get_db_info()
    db_path = db_info['db_path']
    db_port = db_info['db_port']
    db_password = db_info['db_password']
    db_id = db_info['db_public_id']
    r = redis.Redis(host=db_path, port=db_port, db=db_id, password=db_password)
    r.hset(name=host, key=task_id, value=res)

def load_task_info(host, task_id):
    '''
    To get the result of a task through a task
    id.
    :param host:
    :param task_id:
    :return:
    '''
    db_info = get_db_info()
    db_path = db_info['db_path']
    db_port = db_info['db_port']
    db_password = db_info['db_password']
    db_id = db_info['db_public_id']
    r = redis.Redis(host=db_path, port=db_port, db=db_id, password=db_password)
    res = r.hget(name=host,key=task_id)
    return res
