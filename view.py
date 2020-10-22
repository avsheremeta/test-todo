from api import api, db, Task
from flask import render_template,redirect, request, url_for, jsonify,abort,make_response
# from models import Task
from datetime import datetime, timezone
from forms import TaskForm

#convert date.utcnow in date.now
@api.context_processor
def my_utility_processor():
    def utc_to_local(utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime('%d-%m-%Y  (%H:%M:%S)')
    return dict(utc_to_local=utc_to_local)

#create new task
@api.route('/create', methods=['POST', 'GET'])
def create_todo():
    if request.method == 'POST':
        description = request.form['description']
        if description:
            try:
                new_task = Task(description=description, completed=False)
                db.session.add(new_task)
                db.session.commit()
            except:
                print ('Something wrong')
            return redirect(url_for("undone"))     
    form = TaskForm()
    return render_template('create_task.html', form=form)

#edit particular task
@api.route("/edit/<int:todo_id>", methods=['POST', 'GET'])
def edit_todo(todo_id):     
    todo = Task.query.filter_by(id=todo_id).first()
    form = TaskForm(formdata=request.form, obj=todo)
    if request.method == 'POST':
        if todo.description != request.form['description']:
            todo.timestamp_changed = datetime.utcnow()
        form.populate_obj(todo)
        db.session.commit()
        return redirect(url_for('undone'))
    return render_template('edit_task.html', form=form) 

#count of uncompleted tasks
@api.context_processor
def countTaskInWork():
    countWork = db.session.query(Task).filter(Task.completed == False).count()
    return dict(countWork=countWork)

#count of completed tasks
@api.context_processor
def countTaskFinished():
    countDoneWork = db.session.query(Task).filter(Task.completed == True).count()
    return dict(countDoneWork=countDoneWork)

#list of completed tasks
@api.route("/donetask")
def done():
    todo_list = db.session.query(Task).filter(Task.completed == True).all()     
    return render_template('base.html', todo_list=todo_list)



#list of uncompleted tasks
@api.route("/")
def undone():
    todo_list = db.session.query(Task).filter(Task.completed == False).all()
    return render_template('base.html', todo_list=todo_list)

#change the status of the task
@api.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Task.query.filter_by(id=todo_id).first()
    todo.completed = not todo.completed
    todo.timestamp_changed = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("undone"))

#delete task
@api.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Task.query.filter_by(id=todo_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("undone"))