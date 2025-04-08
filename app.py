from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime, nullable=True) 

# Routes
@app.route('/')
def index():
    tasks = Task.query.all()
    
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    # Preprocess tasks to add the "today", "tomorrow" status to the deadline
    for task in tasks:
        if task.deadline:
            task.deadline_display = None
            if task.deadline.strftime('%Y-%m-%d') == today:
                task.deadline_display = f"Today at {task.deadline.strftime('%H:%M')}"
            elif task.deadline.strftime('%Y-%m-%d') == tomorrow:
                task.deadline_display = f"Tomorrow at {task.deadline.strftime('%H:%M')}"
            else:
                task.deadline_display = task.deadline.strftime('%Y-%m-%d %H:%M')
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add():
    task_content = request.form['content']
    task_deadline = request.form['deadline']

    # Convert the deadline string to a datetime object
    deadline = datetime.strptime(task_deadline, '%Y-%m-%dT%H:%M')
    new_task = Task(content=task_content, deadline=deadline)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:id>')
def complete(id):
    task = Task.query.get_or_404(id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>')
def delete(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
