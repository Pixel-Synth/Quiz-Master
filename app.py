import sqlite3
from datetime import timedelta
from flask import Flask, render_template,redirect,url_for, request, session, jsonify
from email_validator import validate_email,EmailNotValidError
from model import db, User, Subject, Topic, Question, Score
app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key="pixelSynth"
db.init_app(app)
app.permanent_session_lifetime = timedelta(days=7)
with app.app_context():
    db.create_all()
@app.route('/',methods=['GET', 'POST'])
def home():
    if 'username' in session:
        username = session['username']
        return render_template('homepage.html', name=username)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        user = User.query.filter((User.username == username) & (User.password == password)).first()
        if user:
            session['username'] = username
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            print(remember, session.permanent)
            return render_template('homepage.html', name=username)
        else:
            return render_template('index.html', error=True, username=username, password=password)
    if request.args.get('logout'):
        return render_template('index.html', logout=True)
    if request.args.get('success'):
        return render_template('index.html', success=True)
    return render_template('index.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        mail = request.form['mail']
        password = request.form['password']
        name = request.form['name']
        confirm_password = request.form['confirm_password']
        existing_user = User.query.filter((User.username == username)).first()
        existing_mail = User.query.filter(User.mail == mail).first()
        if existing_user:
            return render_template('register.html', userError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        if existing_mail:
            return render_template('register.html', mailError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        if password != confirm_password:
            return render_template('register.html', passError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        try:
            valid=validate_email(mail)
        except EmailNotValidError as e:
            return render_template('register.html', mailNotValidError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        new_user = User(username=username, mail=mail, password=password, name=name.capitalize())
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('home', success=True))
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/quiz')
def quiz():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    return render_template('quiz.html', subject=subject, topic=topic)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home', logout=True))

@app.route('/get_questions')
def get_ques():
    tname = request.args.get('topic')
    topic = Topic.query.filter(Topic.tname == tname).first()
    if not topic:
        return jsonify([])
    
    questions = Question.query.filter(tid = topic.tid).all()
    question_list = []
    for question in questions:
        question_list.append({
            'qid': question.qid,
            'question': question.question,
            'option1': question.option1,
            'option2': question.option2,
            'option3': question.option3,
            'option4': question.option4,
            'correct': getattr(question, f'option{question.correct}')
        })
    return jsonify(question_list)

if (__name__ == '__main__'):
    app.run(debug=True)