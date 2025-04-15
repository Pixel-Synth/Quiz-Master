import sqlite3
from datetime import timedelta
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from email_validator import validate_email, EmailNotValidError
from model import db, User, Subject, Topic, Question, Score

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = "pixelSynth"
db.init_app(app)
app.permanent_session_lifetime = timedelta(days=7)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        username = session['username']
        return render_template('homepage.html', name=session['name'], username=username)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember')
        if username == "admin" and password == "pixel-synth":
            session['username'] = username
            session.permanent = bool(remember)
            return redirect(url_for('admin'))
        
        user = User.query.filter((User.username == username) & (User.password == password)).first()
        if user:
            session['username'] = username
            session['name'] = user.name  
            session['email'] = user.mail  
            session.permanent = bool(remember) 
            return render_template('homepage.html', name=user.name, username=username)
        else:
            return render_template('login.html', error=True, username=username, password=password)
    
    if request.args.get('logout'):
        return render_template('login.html', logout=True)
    if request.args.get('success'):
        return render_template('login.html', success=True)
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
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
            valid = validate_email(mail)
        except EmailNotValidError as e:
            return render_template('register.html', mailNotValidError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        
        new_user = User(username=username, mail=mail, password=password, name=name.capitalize())
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', success=True))
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    if 'username' in session:
        return render_template('homepage.html', name=session['name'], username=session['username'])
    return render_template('homepage.html')

@app.route('/quiz')
def quiz():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    return render_template('quiz.html', subject=subject, topic=topic)

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('email', None)
    return redirect(url_for('login', logout=True))

@app.route('/get_questions')
def get_ques():
    tname = request.args.get('topic')
    topic = Topic.query.filter(Topic.tname == tname).first()
    if not topic:
        return jsonify([])
    questions = Question.query.filter(tid=topic.tid).all()
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

@app.route('/profilepage', methods=['GET', 'POST'])
def profilepage():
    if 'username' in session:
        return render_template('profilepage.html', success=request.args.get('success'), name=session['name'], username=session['username'], mail=session['email'])
    return redirect(url_for('home'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if request.method == 'POST':
        username = request.form.get('username')
        name = request.form.get('name')
        user = User.query.filter_by(username=username).first()
        if user and user.username != session['username']:
            return render_template('profilepage.html', userError=True, username=username, name=name, mail=session['email'])
        else:
            user = User.query.filter_by(username=session['username']).first()
            if name:
                user.name = name.capitalize()
            if username:
                user.username = username
                session['username'] = username
            db.session.commit()
            session['name'] = user.name
            session['email'] = user.mail
        db.session.commit()        
        return redirect(url_for('profilepage', success=True, username=username, name=session['name'], mail=session['email']))
    return render_template('index.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        username = session['username']
        current = request.form.get('current_password')
        new = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        user = User.query.filter_by(username=username).first()
        
        if user.password != current:
            return render_template('profilepage.html', passwdError=True, username=username, name=session['name'], mail=session['email'])
        if new != confirm:
            return render_template('profilepage.html', matchError=True, username=username, name=session['name'], mail=session['email'])
        
        user.password = new
        db.session.commit()        
        return redirect(url_for('profilepage', success=True, username=username, name=session['name'], mail=session['email']))
    
    return render_template('index.html')

@app.route('/update_email', methods=['GET', 'POST'])
def update_email():
    if request.method == 'POST':
        username = session['username']
        email = request.form.get('new_email')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        try:
            valid = validate_email(email)
        except EmailNotValidError as e:
            return render_template('profilepage.html', mailNotValidError=True, username=username, name=session['name'], mail=session['email'])
        if user.password != password:
            return render_template('profilepage.html', passwdError=True, username=username, name=session['name'], mail=session['email'])
        existing_mail = User.query.filter(User.mail == email).first()
        if existing_mail and existing_mail!=session['email']:
            return render_template('profilepage.html', mailError=True, username=username, name=session['name'], mail=session['email'])
        user.mail = email
        session['email'] = email
        db.session.commit()        
        return redirect(url_for('profilepage', success=True, username=username, name=session['name'], mail=email))
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin-homepage.html')

@app.route('/adminadd', methods=['GET', 'POST'])
def adminadd():
    if request.method == 'POST':
        question = request.form.get('question')
        option1 = request.form.get('opt-a')
        option2 = request.form.get('opt-b')
        option3 = request.form.get('opt-c')
        option4 = request.form.get('opt-d')
        correct = request.form.get('correct')
        topic = request.args.get('topic')
        t = Topic.query.filter_by(tname=topic).first()
        tid = t.tid
        new_question = Question(tid=tid, question=question, option1=option1, option2=option2, option3=option3, option4=option4, correct=correct)
        db.session.add(new_question)
        db.session.commit()
        return render_template('admin-add-questions.html', success=True, subject=request.args.get('subject'), topic=topic)
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    if subject and topic:

        return render_template('admin-add-questions.html', subject=subject, topic=topic)
    return render_template('index.html')

@app.route('/adminedit')
def adminedit():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    topic_obj = Topic.query.filter_by(tname=topic, subject=subject).first()
    if subject and topic:
        if not topic_obj:
            return render_template("admin-edit-questions.html", questions=[], subject=subject, topic=topic)
        questions = Question.query.filter_by(tid=topic_obj.tid).all()
        return render_template("admin-edit-questions.html", questions=questions, subject=subject, topic=topic)
    return render_template('index.html')

@app.route("/update_question", methods=["POST"])
def update_question():
    data = request.get_json()
    print(data)
    return jsonify({"status": "success"})

@app.route("/delete_question", methods=["POST"])
def delete_question():
    data = request.get_json()
    print(data)
    return jsonify({"status": "deleted"})


if __name__ == '__main__':
    app.run(debug=True)
