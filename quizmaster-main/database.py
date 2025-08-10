from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# User Model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120))
    dob = db.Column(db.Date, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', backref='user', lazy=True)

    # Flask-Login required properties and methods
    @property
    def is_active(self):
        return True  # All users are active by default

    @property
    def is_authenticated(self):
        return True  # Assume the user is authenticated

    @property
    def is_anonymous(self):
        return False  # Regular users are not anonymous

    def get_id(self):
        return str(self.id)  # Return the user's ID as a string

# Subject Model
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade="all, delete-orphan")

# Chapter Model
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade="all, delete-orphan")

# Quiz Model
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date_of_quiz = db.Column(db.Date, nullable=False)
    time_duration = db.Column(db.String(5), nullable=False)  # HH:MM format
    remarks = db.Column(db.String(500))
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade="all, delete-orphan")
    scores = db.relationship('Score', backref='quiz', cascade="all, delete-orphan", lazy=True)

# Question Model

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(500), nullable=False)  # The question statement
    option1 = db.Column(db.String(200), nullable=False)        # Option 1
    option2 = db.Column(db.String(200), nullable=False)        # Option 2
    option3 = db.Column(db.String(200), nullable=True)         # Option 3 (optional)
    option4 = db.Column(db.String(200), nullable=True)         # Option 4 (optional)
    correct_option = db.Column(db.Integer, nullable=False)     # Correct option (1, 2, 3, or 4)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)  # Foreign key to Quiz

    def __repr__(self):
        return f'<Question {self.id}>'
# Score Model
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=datetime.utcnow)