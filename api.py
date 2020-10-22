from flask import Flask, jsonify, abort, make_response, request, url_for, render_template, redirect
from datetime import datetime
from config import Configuration
from flask_sqlalchemy import SQLAlchemy


api = Flask(__name__)
api.config.from_object(Configuration)
db = SQLAlchemy(api)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    description = db.Column(db.String(500))
    timestamp_created = db.Column(db.DateTime, default=datetime.utcnow) 
    timestamp_changed = db.Column(db.DateTime)
    completed = db.Column(db.Boolean)
    

#help function for make list()
def list_all_tasks():
    # tasks = list(db.session.query(Task).all())
    tasks = list(Task.query.all())
    tasks_list=[]
    for task in tasks:
        tasks_list.append({'id': task.id,'description': task.description,'completed': task.completed,
                            'timestamp_created': task.timestamp_created,'timestamp_changed': task.timestamp_changed })
    return tasks_list



tasks = list_all_tasks()

# get all tasks
@api.route('/todo/api/tasks', methods=['GET'])
def get_tasks():  
    return jsonify({'tasks': list(map(make_public_task, tasks))})

#get particular task
@api.route('/todo/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})


@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#create task
@api.route('/todo/api/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'description' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        # 'title': request.json['title'],
        'description': request.json.get('description', ""),
        'completed': False , 
        'timestamp_created': datetime.utcnow(),
        'timestamp_changed': request.json.get('timestamp_changed', "")     
    }
    tasks.append(task)
    return jsonify({'task': task}), 201

#update task
@api.route('/todo/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not str:
        abort(400)
    if 'commited' in request.json and type(request.json['commited']) is not bool:
        abort(400)
    task[0]['timestamp_created'] = request.json.get('timestamp_created', task[0]['timestamp_created'])
    task[0]['timestamp_changed'] = request.json.get('timestamp_changed', task[0]['timestamp_changed'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['commited'] = request.json.get('commited', task[0]['commited'])
    return jsonify({'task': task[0]})

#delete_task
@api.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

#make url instead of id
def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task



# if __name__ == '__main__':
#     api.run()

