from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/goals/<goal>/')
def goals(goal):
    return render_template('goal.html')

@app.route('/profiles/<teacher_id>/')
def teachers(teacher_id):
    return render_template('profile.html')

@app.route('/request/')
def request():
    return render_template('request.html')

@app.route('/request_done/')
def done():
    return render_template('request_done.html')

@app.route('/booking/<teacher_id>/')
def book(teacher_id):
    return render_template('booking.html')

@app.route('/booking_done/')
def book_done():
    return render_template('booking_done.html')

app.run()