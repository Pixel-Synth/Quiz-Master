import sqlite3
from datetime import timedelta
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from email_validator import validate_email, EmailNotValidError
from model import db, User, Subject, Topic, Question, Score
from collections import defaultdict

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
        return redirect(url_for('homepage', name=session['name'], username=username, courses = get_courses()))
    
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
            return render_template('homepage.html', name=user.name, username=username, courses=get_courses())
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
        if len(password) < 8:
            return render_template('register.html', lengthError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        digit=False
        upper=False
        lower=False
        special=False
        for i in password:
            if i.isdigit():
                digit=True
            if i.isupper():
                upper=True
            if i.islower():
                lower=True
            if i in ['@','!','#','$','%','^','&','*']:
                special=True
        if not digit:
            return render_template('register.html', numberError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        if not upper:
            return render_template('register.html', upperCaseError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        if not lower:
            return render_template('register.html', lowerCaseError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        if not special:
            return render_template('register.html', specialCharError=True, username=username, mail=mail, password=password, name=name, confirm_password=confirm_password)
        new_user = User(username=username, mail=mail, password=password, name=name.capitalize())
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login', success=True))
    return render_template('register.html')

@app.route('/homepage')
def homepage():
    if 'username' in session:
        return render_template('homepage.html', name=session['name'], username=session['username'], courses =get_courses())
    return redirect(url_for('home'))

@app.route('/quiz')
def quiz():
    subject = request.args.get('subject')
    topic = request.args.get('topic')
    if not subject or not topic:
        return redirect(url_for('home'))
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
    if Question.query.count() > 0:
        questions = Question.query.filter(Question.tid == topic.tid).all()
        question_list = []
        for question in questions:
            question_list.append({
                'qid': question.qid,
                'question': question.question,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct': question.correct
            })
        return jsonify(question_list)
    return jsonify([])

@app.route('/profilepage', methods=['GET', 'POST'])
def profilepage():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        quizzes_taken = Score.query.filter_by(uid=user.uid).count()
        total_score = db.session.query(db.func.sum(Score.score)).filter_by(uid=user.uid).scalar() or 0
        avg_score = total_score / quizzes_taken if quizzes_taken > 0 else 0
        avg_score = round(avg_score, 2)
        highest_score = db.session.query(db.func.max(Score.score)).filter_by(uid=user.uid).scalar() or 0
        total_time = db.session.query(db.func.sum(Score.time)).filter_by(uid=user.uid).scalar() or 0
        minutes = total_time // 60
        seconds = total_time % 60
        if minutes < 10:
            minutes = f"0{minutes}"
        if seconds < 10:
            seconds = f"0{seconds}"
        return render_template('profilepage.html', success=request.args.get('success'), name=session['name'], username=session['username'], mail=session['email'], quizzes_taken=quizzes_taken, avg_score=avg_score, highest_score=highest_score, total_time=f"{minutes}:{seconds}")
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

@app.route('/admin', methods = ['GET', 'POST'])
def admin():
    if not session.get('username'):
        return redirect(url_for('home'))
    if session.get('username') != "admin":
        return redirect(url_for('home'))
    scores = Score.query.all()

    topic_scores = defaultdict(list)
    time_data = defaultdict(lambda: defaultdict(list))
    for score in scores:
        user = score.user
        topic = score.topic
        subject = topic.subject

        topic_scores[topic.tname].append((user.username, score.score))
        time_data[subject.sname][topic.tname].append(score.time)

    topic_data = {
        topic: {
            "labels": [u for u, _ in vals],
            "scores": [s for _, s in vals]
        } for topic, vals in topic_scores.items()
    }

    student_status = [
        {
            "username": user.username,
            "uid": user.uid,
            "name": user.name,
            "email": user.mail,
            "status": f"{len(user.scores)} quizzes completed"
        }
        for user in User.query.all()
    ]
    course_list = []
    Subjects = Subject.query.all()
    for subject in Subjects:
        topic_list = {"subject":subject.sname,"topics":[]}
        Topics = Topic.query.filter(Topic.sid == subject.sid).all()
        for topic in Topics:
            topic_list["topics"].append(topic.tname)
        course_list.append(topic_list)
    return render_template(
        'admin-homepage.html',
        topic_data=topic_data,
        time_data=time_data,
        student_status=student_status,
        courses=course_list
    )

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
    topic_obj = Topic.query.filter(Topic.tname==topic).first()
    if subject and topic:
        if not topic_obj:
            return render_template("admin-edit-questions.html", questions=[], subject=subject, topic=topic)
        questions = Question.query.filter_by(tid=topic_obj.tid).all()
        return render_template("admin-edit-questions.html", questions=questions, subject=subject, topic=topic)
    return render_template('index.html')

@app.route("/update_question", methods=["POST"])
def update_question():
    data = request.get_json()
    qid = data.get("id")
    question = data.get("question")
    option1 = data.get("option1")
    option2 = data.get("option2")
    option3 = data.get("option3")
    option4 = data.get("option4")
    correct = data.get("correct")
    question_obj = Question.query.filter(Question.qid==qid).first()
    if not question_obj:
        return jsonify({"status": "not found"})
    question_obj.question = question
    question_obj.option1 = option1
    question_obj.option2 = option2
    question_obj.option3 = option3
    question_obj.option4 = option4
    question_obj.correct = correct
    
    db.session.commit()
    return jsonify({"status": "success"})

@app.route("/delete_question", methods=["POST"])
def delete_question():
    data = request.get_json()
    qid = data.get("id")
    question = Question.query.filter_by(qid=qid).first()
    if not question:
        return jsonify({"status": "not found"})
    db.session.delete(question)
    db.session.commit()
    return jsonify({"status": "deleted"})

@app.route('/update_score', methods=['POST'])
def update_score():
    if request.method == 'POST':
        username = session['username']
        topic = request.args.get('topic')
        score = float(request.args.get('score'))
        score = round(score, 2)
        time = int(request.args.get('time'))
        user = User.query.filter_by(username=username).first()
        topic_obj = Topic.query.filter_by(tname=topic).first()
        if user and topic_obj:
            new_score = Score(uid=user.uid, tid=topic_obj.tid, score=score, time=time)
            db.session.add(new_score)
            db.session.commit()
            return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app.route('/sub', methods=['GET'])
def sub():
    courses = get_courses()
    return render_template('admin-edit-subjects.html', courses=courses)

@app.route('/topic', methods=['GET'])
def topic():
    topics = get_courses()
    return render_template('admin-edit-topics.html', courses=topics)

@app.route('/add_sub', methods=['POST'])
def add_sub():
    if request.method == 'POST':
        subject_name = request.form.get('subject-input')
        existing_subject = Subject.query.filter_by(sname=subject_name).first()
        if existing_subject:
            courses = get_courses()
            return render_template('admin-edit-subjects.html', error="Subject "+subject_name+" already exists", courses=courses)
        new_subject = Subject(sname=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        courses = get_courses()    
        return render_template('admin-edit-subjects.html', successAddSub="Successfully Added Subject "+subject_name, courses=courses)
    return redirect(url_for('home'))

@app.route('/remove_sub', methods=['POST'])
def remove_sub():
    if request.method == 'POST':
        subject_name = request.form.get('subject-select')
        if not subject_name:
            courses = get_courses()
            return render_template('admin-edit-subjects.html', error="No Subject Selected", courses=courses)
        subject = Subject.query.filter_by(sname=subject_name).first()
        if subject:
            db.session.delete(subject)
            db.session.commit()
        courses = get_courses()    
        return render_template('admin-edit-subjects.html', successRemoveSub="Successfully Removed Subject "+subject_name, courses=courses)
    return redirect(url_for('home'))

@app.route('/add_topic', methods=['POST'])
def add_topic():
    if request.method == 'POST':
        topic_name = request.form.get('topic-input')
        subject_name = request.form.get('subject-select')
        if not subject_name:
            return render_template('admin-edit-topics.html', error="No Subject Selected", courses=get_courses(), topic_name=topic_name)
        existing_topic = Topic.query.filter_by(tname=topic_name).first()
        if existing_topic:
            return render_template('admin-edit-topics.html', error="Topic "+topic_name+" already exists", courses=get_courses(), topic_name=topic_name)
        subject = Subject.query.filter_by(sname=subject_name).first()
        new_topic = Topic(tname=topic_name, sid=subject.sid)
        db.session.add(new_topic)
        db.session.commit()
        return render_template('admin-edit-topics.html', successAddTopic="Successfully Added Topic "+topic_name+" to Subject "+subject_name, courses=get_courses())
    return redirect(url_for('home'))

@app.route('/remove_topic', methods=['POST'])
def remove_topic():
    if request.method == 'POST':
        topic_name = request.form.get('topic-select')
        if not topic_name:
            return render_template('admin-edit-topics.html', error="No Topic Selected",courses=get_courses())
        topic = Topic.query.filter_by(tname=topic_name).first()
        subject = topic.subject
        if topic:
            db.session.delete(topic)
            db.session.commit()
        return render_template('admin-edit-topics.html', successAddTopic="Successfully Removed Topic "+topic_name+" from Subject "+subject.sname, courses=get_courses())
    return redirect(url_for('home'))

def get_courses():
    course_list = []
    Subjects = Subject.query.all()
    for subject in Subjects:
        topic_list = {"subject":subject.sname,"topics":[]}
        Topics = Topic.query.filter(Topic.sid == subject.sid).all()
        for topic in Topics:
            topic_list["topics"].append(topic.tname)
        course_list.append(topic_list)
    return course_list


if __name__ == '__main__':
    app.run(debug=True)
