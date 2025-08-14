from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SelectField, TextAreaField, IntegerField, DateTimeField, FloatField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from models import UserRole

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[(role.value, role.value.title()) for role in UserRole], validators=[DataRequired()])
    
    # NGO-specific fields
    ngo_name = StringField('NGO Name', validators=[Optional(), Length(max=100)])
    ngo_description = TextAreaField('NGO Description', validators=[Optional()])

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=200)])
    points_per_slot = IntegerField('Points per Slot', validators=[DataRequired(), NumberRange(min=1, max=100)])
    required_skills = TextAreaField('Required Skills', validators=[Optional()])

class TimeSlotForm(FlaskForm):
    start_time = DateTimeField('Start Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_time = DateTimeField('End Time', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    max_volunteers = IntegerField('Max Volunteers', validators=[DataRequired(), NumberRange(min=1, max=20)])

class VerificationUploadForm(FlaskForm):
    file = FileField('Upload Verification Photo', validators=[DataRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    notes = TextAreaField('Notes', validators=[Optional()])

class DonationForm(FlaskForm):
    amount = FloatField('Donation Amount', validators=[DataRequired(), NumberRange(min=1)])
    message = TextAreaField('Message', validators=[Optional()])
    is_anonymous = BooleanField('Donate Anonymously')

class VerificationReviewForm(FlaskForm):
    status = SelectField('Status', choices=[('approved', 'Approved'), ('rejected', 'Rejected')], validators=[DataRequired()])
    notes = TextAreaField('Review Notes', validators=[Optional()])
