#Downtiser
'''The main logic unit of server port, which is used
to interact with client and database
'''
import pika, redis, threading
from RabbitMQ_async.RabbitMQ_async_server.conf import SETTINGS
from RabbitMQ_async.RabbitMQ_async_server.core import data_handler
class RPCServer(object):
    '''The class is used to instantiate a server object to receive
    command from client and store the result in database
    '''
    def __init__(self, host):
        '''
        To prepare some work for start connection
        :param host:
        '''
        self.command_dict = {
            'get_fisher_number':self.judge_fisher_number,
            'redis_ctl':self.redis_ctl,
            'check':self.check
        }
        self.host = host
        self.__credential = pika.PlainCredentials(SETTINGS.RabbitMQ_host_info[host]['user'],
                                                  SETTINGS.RabbitMQ_host_info[host]['password']
                                                  )


    def start_server(self):
        '''
        Start the server port, prepare to receive command
        :return:
        '''
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            SETTINGS.RabbitMQ_host_info[self.host]['addr'],
            virtual_host='/',
            credentials=self.__credential
        )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='command_queue', durable=True)
        self.channel.basic_consume(
            self.command_handler,
            queue='command_queue'
        )
        print('%s: Start serving.....'%self.host)
        self.channel.start_consuming()

    def command_handler(self, channel, method, properties, body):
        '''
        To deal with the command sent by client
        :param channel:
        :param method:
        :param properties:
        :param body:
        :return:
        '''
        self.reply_queue = properties.reply_to
        task_id = properties.correlation_id

        cmd_list = body.decode().split()

        self.command_dict[cmd_list[0]](cmd_list, task_id)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def judge_fisher_number(self, cmd_list, task_id):
        '''
        To judge a number is a fisher number or not.
        Just for fun.
        :param cmd_list:
        :param task_id:
        :return:
        '''
        if len(cmd_list) != 2:
            res = 'invalid input!'
            data_handler.dump_task_info(self.host, task_id, res)
            return
        n = int(cmd_list[1])
        multipliers = []
        i = 2
        while i <= n / 2:
            if n % i == 0:
                multipliers.append(i)
            i += 1

        multipliers.append(n)
        sum = 1
        for multiplier in multipliers:
            sum *= multiplier

        if sum == n ** 3:
            for i, item in enumerate(multipliers):
                multipliers[i] = str(item)
            res = '%s is a fisher number: ' % n + '*'.join(multipliers) + '=' + '%s^3' % n

        else:
            res = '%s is not a fisher number' % n
        data_handler.dump_task_info(self.host, task_id, res)
    def redis_ctl(self, cmd_list, task_id):
        '''
        To manage the client's own database through the
        command
        :param cmd_list:
        :param task_id:
        :return:
        '''
        cmd_len = len(cmd_list)
        if cmd_len <= 2:
            res = 'Invalid command!'
            data_handler.dump_task_info(self.host, task_id, res)
            return
        operation = cmd_list[1]
        option_list = cmd_list[2:]
        db_info = data_handler.get_db_info()
        db_path = db_info['db_path']
        db_port = db_info['db_port']
        db_passwd = db_info['db_password']
        db_id = SETTINGS.RabbitMQ_host_info[self.host]['db_id']
        r = redis.Redis(host=db_path, port=db_port, db=db_id, password=db_passwd)
        try:
            if hasattr(r, operation):
                fun = getattr(r,operation)
                if len(option_list) == 1:
                    res = fun(option_list[0])
                elif len(option_list) == 2:
                    res = fun(option_list[0], option_list[1])
                elif len(option_list) == 3:
                    res = fun(option_list[0], option_list[1], option_list[3])
                if res == None:
                    res = '(None)'
            else:
                res = 'redis_ctl has no attribute %s, please check your input!'%operation
        except (TypeError, ValueError) :
            res = 'invalid option!'
        except Exception:
            res = 'Unknown Error!'

        data_handler.dump_task_info(self.host, task_id, res)

    def check(self, cmd_list, task_id):
        '''
        To get the result from database through task_id and
        publish it to client
        :param cmd_list:
        :param task_id:
        :return:
        '''
        if len(cmd_list) > 2:
            res = 'Invalid input! You can only check onn result at one time'
        db_info = data_handler.get_db_info()
        db_path = db_info['db_path']
        db_port = db_info['db_port']
        db_password = db_info['db_password']
        db_id = db_info['db_public_id']
        r = redis.Redis(host=db_path, port=db_port, db=db_id, password=db_password)
        res = r.hget(self.host, cmd_list[1])
        if res == None:
            res = '(None)'
        self.channel.basic_publish(
            exchange='',
            routing_key=self.reply_queue,
            properties=pika.BasicProperties(
                correlation_id=task_id,
                delivery_mode=2
            ),
            body=res
        )






