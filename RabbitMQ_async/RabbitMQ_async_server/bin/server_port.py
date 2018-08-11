#Downtiser
'''The main port of server, Just run the program and wait for log in'''
from RabbitMQ_async.RabbitMQ_async_server.core import server_main
from RabbitMQ_async.RabbitMQ_async_server.conf import SETTINGS
import threading



if __name__ == '__main__' :
    server_list = []
    thread_list = []

    for key in SETTINGS.RabbitMQ_host_info:
        server_obj = server_main.RPCServer(key)
        server_list.append(server_obj)
    for obj in server_list:
        t = threading.Thread(target=obj.start_server,)
        t.start()