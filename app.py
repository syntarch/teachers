from flask import Flask, render_template, request
import json

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import InputRequired

app = Flask(__name__)
app.secret_key = 'CSRF_will_be_stopped'

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
    rating = db.Column(db.Float)
    booking = db.relationship('Book', back_populates='teacher')


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
    client_name = db.Column(db.String())
    client_phone = db.Column(db.String())
    client_weekday = db.Column(db.String())
    client_time = db.Column(db.String())
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    client_teacher = db.Column(db.String())
    teacher = db.relationship('Teacher', back_populates='booking')


class BookingForm(FlaskForm):
    client_name = StringField('Ваше имя', [InputRequired(message='Поле не может быть пустым')])
    client_phone = StringField('Номер телефона', [InputRequired(message='Поле не может быть пустым')])
    client_weekday = HiddenField()
    client_time = HiddenField()
    teacher_id = HiddenField()
    client_teacher = HiddenField()
    submit = SubmitField('Поехали формы!')


db.create_all()

with open('teachers.json', 'r', encoding='utf-8') as f:
    teachers_info = f.read()
teachers_list = json.loads(teachers_info)

with open('goals.json', 'r', encoding='utf-8') as v:
    goals_info = v.read()
goals_list = json.loads(goals_info)

#this block fills the db with the teachers data
# for teacher in teachers_list:
#     imported_teacher = Teacher(name=teacher['name'],
#                                about=teacher['about'],
#                                price=teacher['price'],
#                                goals=','.join(teacher['goals']),
#                                picture=teacher['picture'],
#                                rating=teacher['rating'])
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
    appropriate_teachers_db = db.session.query(Teacher).filter(Teacher.goals.contains(goal))
    appropriate_teachers = appropriate_teachers_db.all()
    return render_template('goal.html', goal_ru=goal_ru, teachers=appropriate_teachers)

@app.route('/profiles/<int:teacher_id>/')
def teachers(teacher_id):
    selected_teacher = db.session.query(Teacher).get_or_404(teacher_id)
    week = {'mon': 'Понедельник', 'tue': 'Вторник', 'wed': 'Среда', 'thu': 'Четверг', 'fri': 'Пятница',
            'sat': 'Суббота', 'sun': 'Воскресенье'}
    for teacher in teachers_list:
        if teacher['id'] == teacher_id:
            teacher_schedule = teacher['free']
    time_available = {}
    for day, times in teacher_schedule.items():
        time_available[day] = {}
        for time, status in times.items():
            if status is True:
                time_available[day][time] = True
    return render_template('profile.html',
                           name=selected_teacher.name, rating=selected_teacher.rating,
                           price=selected_teacher.price, about=selected_teacher.about, picture=selected_teacher.picture,
                           teacher_goals=selected_teacher.goals, id=selected_teacher.id, week=week,
                           schedule=time_available)

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

@app.route('/booking/<int:teacher_id>/<aday>/<atime>/', methods=['GET', 'POST'])
@app.route('/booking_done/', methods=['POST'])
def book(teacher_id, aday, atime):
    form = BookingForm()
    if request.method == 'POST' and form.validate_on_submit():
        client_name = form.client_name.data
        client_phone = form.client_phone.data
        client_weekday = form.client_weekday.data
        client_time = form.client_time.data
        teacher_id = form.teacher_id.data
        client_teacher = form.client_teacher.data
        new_booking = Book(client_weekday=client_weekday,
                           client_time=client_time,
                           client_name=client_name,
                           client_phone=client_phone,
                           teacher_id=teacher_id,
                           client_teacher=client_teacher)
        db.session.add(new_booking)
        db.session.commit()
        return render_template('booking_done.html',
                           day=client_weekday,
                           time=client_time,
                           name=client_name,
                           phone=client_phone,
                           teacher=client_teacher)
    else:
        teacher_db = db.session.query(Teacher).get_or_404(teacher_id)
        return render_template('booking.html', name=teacher_db.name, day=aday, time=atime, id=teacher_id, form=form)


if __name__ == '__main__':
    app.run(debug=True)