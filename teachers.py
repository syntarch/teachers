from flask import Flask, render_template
import json

with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers_info = f.read()
teachers_list = json.loads(teachers_info)

with open('goals.json', 'r', encoding='utf-8') as v:
    goals_info = v.read()
goals_list = json.loads(goals_info)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/goals/<goal>/')
def goals(goal):
    return render_template('goal.html')

@app.route('/profiles/<int:teacher_id>/')
def teachers(teacher_id):
    for prepod in teachers_list:
        if prepod['id'] == teacher_id:
            name = prepod['name']
            rating = prepod['rating']
            price = prepod['price']
            about = prepod['about']
            picture = prepod['picture']
            for_goals = prepod['goals']
            timetable = prepod['free']
    teacher_goals = []
    time_available = {}
    for day, times in timetable.items():
        time_available[day] = {}
        for time, status in times.items():
            if status is True:
                time_available[day][time] = True
    for x in goals_list:
        if x in for_goals:
            teacher_goals += [goals_list[x]]
    week = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница', 'sat': 'Суббота',
            'sun': 'Воскресенье'}
    return render_template('profile.html', name=name, rating=rating, price=price, about=about, picture=picture,
                           teacher_goals=teacher_goals, schedule=time_available, week=week)

@app.route('/request/')
def request():
    return render_template('request.html')

@app.route('/request_done/')
def done():
    return render_template('request_done.html')

@app.route('/booking/<teacher_id>/<aday>/<atime>/')
def book(teacher_id):
    return render_template('booking.html')

@app.route('/booking_done/')
def book_done():
    return render_template('booking_done.html')

app.run()