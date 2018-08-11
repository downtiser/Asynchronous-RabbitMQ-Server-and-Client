#Downtiser
'''The main logic unit of client port, which can receive command and deal with it,
then send the request to server port and can also receive result from server through
using specific command.
'''
import pika, threading, uuid, time
from RabbitMQ_async.RabbitMQ_async_client.conf import SETTINGS
'''The list is to store valid command'''
command_list = ['get_fisher_number', 'redis_ctl', 'check']
class RPCClient(object):
    '''The class is used to instantiate a object which can connect with the RabbitMQ
    server and interact with the server in an asynchronous way.
    '''
    def __init__(self, host, command, task_id):
        '''
        Initialize the object, finish some connection task.
        :param host:
        :param command:
        :param task_id:
        '''
        self.host = host
        self.command = command

        self.__credential = pika.PlainCredentials(
            username=SETTINGS.RabbitMQ_info[self.host]['user'],
            password=SETTINGS.RabbitMQ_info[self.host]['password']
        )
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=SETTINGS.RabbitMQ_info[self.host]['addr'],
            port=SETTINGS.RabbitMQ_info[self.host]['port'],
            virtual_host='/',
            credentials=self.__credential
        )
        )
        self.channel = self.connection.channel()
        self.check_queue = self.channel.queue_declare(exclusive=True)
        self.check_queue_name = self.check_queue.method.queue
        self.task_id = task_id


    def publish_command(self):
        '''
        Publish the command to the server to make server push the
        result into the database
        :return:
        '''
        self.channel.basic_publish(
            exchange='',
            routing_key='command_queue',
            properties=pika.BasicProperties(
                reply_to=self.check_queue_name,
                correlation_id=self.task_id,
                delivery_mode=2
            ),
            body=self.command
        )
        cmd_list = self.command.split()
        if cmd_list[0] == 'check':
            self.check_result(cmd_list)

    def check_result(self, command_list):
        '''
        To subscribe the result of previous task through
        the task_id
        :param command_list:
        :return:
        '''
        if len(command_list) > 2:
            print('You can only check one task at one time!')
            return
        res_id = command_list[1]
        self.channel.basic_consume(
            self.get_result,
            queue=self.check_queue_name
        )
        self.channel.start_consuming()
    def get_result(self, channel, method, properties, body):
        '''
        To receive the explicit result of the task
        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        '''
        if properties.correlation_id == self.task_id:
            print('[%s]:'%self.host,body.decode())

def help():
    '''
    For user to get command help
    :return:
    '''
    print('----Command list----')
    print('To judge a fisher number>>>get_fisher_number number --host host1 host2......')
    print('To manage your own database>>>redis_ctl operation args --host host1 host2......')
    print('To check the result of your task>>>check task_id --host host1 host2.....')

def command_solver():
    '''
    To deal with the command the client input, and convert it into
    the client object.
    :return:
    '''
    while True:
        command = input('>>>').strip()
        cmd_list = command.lower().split()
        if cmd_list[0] == 'help':
            help()
            continue
        if cmd_list[0] not in command_list:
            print('The command [%s] does not exist! Please check your input!')
            continue
        if '--host' in cmd_list:
            index = cmd_list.index('--host')
        else:
            print('please input "--host" to specify hosts!')
            continue
        host_list = cmd_list[index+1:]
        solved_cmd_list = cmd_list[0:index]
        solved_cmd = ' '.join(solved_cmd_list)
        client_obj_list = []
        task_id = str(uuid.uuid4())
        if solved_cmd_list[0].lower() != 'check':
            print('This is your Task id, you can check the result of the task through the task id>>>%s'%task_id)
        for host in host_list:
            if host in SETTINGS.RabbitMQ_info:
                obj = RPCClient(host, solved_cmd, task_id)
                client_obj_list.append(obj)
            else:
                print("The host %s does not exist! The message to this host won't reach!"%host)
        for client in client_obj_list:
            t = threading.Thread(target=client.publish_command)
            t.start()
        time.sleep(1)





















