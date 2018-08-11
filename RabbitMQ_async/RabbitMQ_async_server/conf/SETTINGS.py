#Downtiser
'''Store the settings of host address, password, database information, etc'''
import os
RabbitMQ_host_info = {
    'localhost':{
        'user':'downtiser',
        'password':'gu996080',
        'addr':'localhost',
        'port':5672,
        'db_id':1

    },
    '192.168.10.30':{
        'user':'downtiseme',
        'password':'gu996080',
        'addr':'192.168.10.30',
        'port':5672,
        'db_id':2

    }

}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

db_info = {
    'db_name':'data',
    'db_engine':'Redis',
    'db_path':'192.168.10.30',
    'db_password':'gu996080',
    'db_port':6379,
    'db_public_id':0
}