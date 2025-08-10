from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, DateField, TextAreaField, 
    SubmitField, SelectField, IntegerField, RadioField
)
from wtforms.validators import DataRequired, Email, Length, ValidationError, EqualTo, Regexp
from datetime import datetime
from database import User

# User Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

# User Registration Form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Confirm Password", 
        validators=[DataRequired(), EqualTo('password', message="Passwords must match.")]
    )
    full_name = StringField("Full Name", validators=[DataRequired()])
    qualification = StringField("Qualification", validators=[DataRequired()])
    dob = DateField("Date of Birth", format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("This email is already in use. Please use a different one.")
    
    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("This username is already taken. Please choose a different one.")

        
# Subject Management Form
class SubjectForm(FlaskForm):
    name = StringField("Subject Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")

# Chapter Management Form
class ChapterForm(FlaskForm):
    name = StringField("Chapter Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    subject_id = SelectField("Select Subject", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")

# Quiz Creation Form
class QuizForm(FlaskForm):
    title = StringField("Quiz Title", validators=[DataRequired()])
    subject_id = SelectField("Select Subject", coerce=int, validators=[DataRequired()])  # Add this field
    chapter_id = SelectField("Select Chapter", coerce=int, validators=[DataRequired()])
    date_of_quiz = DateField("Quiz Date", format='%Y-%m-%d', validators=[DataRequired()])
    duration = StringField(
        "Duration (HH:MM)", 
        validators=[
            DataRequired(),
            Regexp(r'^\d{2}:\d{2}$', message="Duration must be in HH:MM format.")
        ]
    )
    remarks = TextAreaField("Remarks")
    submit = SubmitField("Save")

    def validate_date_of_quiz(self, date_of_quiz):
        if date_of_quiz.data < datetime.today().date():
            raise ValidationError("Quiz date must be today or a future date.")

# Question Management Form
class QuestionForm(FlaskForm):
    question_text = TextAreaField("Question", validators=[DataRequired()])
    option1 = StringField("Option 1", validators=[DataRequired()])
    option2 = StringField("Option 2", validators=[DataRequired()])
    option3 = StringField("Option 3")
    option4 = StringField("Option 4")
    correct_option = RadioField(
        "Correct Answer", 
        choices=[(1, "Option 1"), (2, "Option 2"), (3, "Option 3"), (4, "Option 4")], 
        coerce=int, 
        validators=[DataRequired()]
    )
    submit = SubmitField("Save")
