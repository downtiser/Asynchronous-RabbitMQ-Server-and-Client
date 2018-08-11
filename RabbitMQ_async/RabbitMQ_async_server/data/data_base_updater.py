#Downtiser
import json
task_data = {
    'localhost':{},
    '192.168.10.30':{}
}
f = open('task_data.json', 'w')
f.write(json.dumps(task_data))
f.close()