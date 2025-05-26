from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class UploadFileForm(FlaskForm):
    file = FileField('Select File', validators=[FileRequired()])
    folder_id = SelectField('Folder', coerce=int)
    submit = SubmitField('Upload')

class CreateFolderForm(FlaskForm):
    name = StringField('Folder Name', validators=[DataRequired(), Length(min=1, max=255)])
    parent_id = SelectField('Parent Folder', coerce=int)
    submit = SubmitField('Create Folder')

class ShareFileForm(FlaskForm):
    email = StringField('User Email', validators=[DataRequired(), Email()])
    permission = SelectField('Permission', 
                           choices=[('view', 'Can View'), ('edit', 'Can Edit')])
    submit = SubmitField('Share')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class RenameFileForm(FlaskForm):
    filename = StringField('New Name', validators=[DataRequired(), Length(min=1, max=255)])
    submit = SubmitField('Rename')
