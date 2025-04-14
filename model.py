from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    uid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mail = db.Column(db.String, unique=True, nullable=False)
    

