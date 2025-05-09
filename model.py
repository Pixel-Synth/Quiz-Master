from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, unique=True, nullable=False)
    scores = db.relationship('Score', backref='user', lazy=True)

class Subject(db.Model):
    __tablename__ = "subject"
    sid = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String, unique=True, nullable=False)
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade="all, delete")

class Topic(db.Model):
    __tablename__ = "topic"
    tid = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.Integer, db.ForeignKey('subject.sid'), nullable=False)
    tname = db.Column(db.String, nullable=False)
    questions = db.relationship('Question', backref='topic', lazy=True, cascade="all, delete")
    scores = db.relationship('Score', backref='topic', lazy=True, cascade="all, delete")

class Question(db.Model):
    __tablename__ = "question"
    qid = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, db.ForeignKey('topic.tid'), nullable=False)
    question = db.Column(db.String, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    correct = db.Column(db.Integer, nullable=False)

class Score(db.Model):
    __tablename__ = "score"
    sid = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.uid'), nullable=False)
    tid = db.Column(db.Integer, db.ForeignKey('topic.tid'), nullable=False)
    score = db.Column(db.Double, nullable=False)
    time = db.Column(db.Integer, default=db.func.current_timestamp())