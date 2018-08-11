#Downtiser
'''The main port of client, Just run the program and input command'''
from RabbitMQ_async.RabbitMQ_async_client.core import client_main
if __name__ == '__main__':
    client_main.command_solver()