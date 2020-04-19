from flask import Flask, render_template, request
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    about = db.Column(db.String())
    price = db.Column(db.Integer)
    goals = db.Column(db.String())
    picture = db.Column(db.String())


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    phone = db.Column(db.String())
    goal = db.Column(db.String())
    time_to_learn = db.Column(db.String())


class Book(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.String())
    time = db.Column(db.String())
    teacher = db.Column(db.String())
    client_name = db.Column(db.String())
    client_phone = db.Column(db.String())


db.create_all()

with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers_info = f.read()
teachers_list = json.loads(teachers_info)

with open('goals.json', 'r', encoding='utf-8') as v:
    goals_info = v.read()
goals_list = json.loads(goals_info)

#this block fill the db with the teachers data
# for teacher in teachers_list:
#     imported_teacher = Teacher(name=teacher['name'],
#                                about=teacher['about'],
#                                price=teacher['price'],
#                                goals=' '.join(teacher['goals']),
#                                picture=teacher['picture'])
#     db.session.add(imported_teacher)
# db.session.commit()


@app.route('/')
def index():
    random_teachers_db_1 = db.session.query(Teacher).order_by(func.random()).limit(6)
    random_teachers_db_2 = random_teachers_db_1.all()
    return render_template('index.html', random_teachers=random_teachers_db_2)

@app.route('/all_teachers')
def all_teachers():
    all_teachers_from_db = db.session.query(Teacher).all()
    return render_template('all_teachers.html', teachers=all_teachers_from_db)

@app.route('/goals/<goal>/')
def goals(goal):
    goal_ru = goals_list[goal]
    appropriate_teachers = [teacher for teacher in teachers_list if goal in teacher['goals']]
    appropriate_teachers_sorted = sorted(appropriate_teachers, key=lambda k: k['rating'], reverse=True)
    print(appropriate_teachers_sorted)
    return render_template('goal.html', goal_ru=goal_ru, teachers=appropriate_teachers_sorted)

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
                           teacher_goals=teacher_goals, schedule=time_available, week=week, id=teacher_id)

@app.route('/request/')
def my_request():
    return render_template('request.html')

@app.route('/request_done/', methods=['GET'])
def done():
    goal_en = request.args['goal']
    learn_time = request.args['time']
    name = request.args['name']
    phone = request.args['phone']
    goals_dict = {'travel': 'Для путешествий', 'learn': 'Для школы', 'work': 'Для работы', 'move': 'Для переезда'}
    goal_ru = goals_dict[goal_en]
    request_for_db = Request(name=name, phone=phone, goal=goal_en, time_to_learn=learn_time)
    db.session.add(request_for_db)
    db.session.commit()
    return render_template('request_done.html', goal=goal_ru, time=learn_time, name=name, phone=phone)

@app.route('/booking/<int:teacher_id>/<aday>/<atime>/')
def book(teacher_id, aday, atime):
    for prepod in teachers_list:
        if prepod['id'] == teacher_id:
            name = prepod['name']

    return render_template('booking.html', name=name, day=aday, time=atime, id=teacher_id)


@app.route('/booking_done/', methods=['GET'])
def book_done():
    weekday = request.args['clientWeekday']
    time = request.args['clientTime']
    teacher = request.args['clientTeacher']
    client_name = request.args['clientName']
    phone = request.args['clientPhone']
    new_booking = {'clientWeekday': weekday, 'clientTime': time, 'clientTeacher': teacher,
                   'clientName': client_name, 'clientPhone': phone}

    with open('booking.json', 'r', encoding='utf-8') as bk:
        booking_list_json = bk.read()
    booking_list = json.loads(booking_list_json)
    booking_list += [new_booking]
    booking_list_json = json.dumps(booking_list)
    with open('booking.json', 'w', encoding='utf-8') as bkng:
        bkng.write(booking_list_json)

    return render_template('booking_done.html',
                           day=weekday, time=time, name=client_name, phone=phone, teacher=teacher)


if __name__ == '__main__':
    app.run(debug=True)