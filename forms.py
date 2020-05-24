from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Email, Length, EqualTo, ValidationError


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])
    
class EditProfileForm(FlaskForm):
    """Form for editing user profile"""
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    email = StringField('(Optional) E-mail', validators=[Email()])    
    image_url = StringField('(Optional) Profile Image URL')
    header_image_url = StringField('(Optional) Background Image URL')
    bio = StringField('(Optional) Bio')    
    location = StringField('(Optional) Location')
    
class ChangePasswordForm(FlaskForm):
    """Form for changing password"""    
    oldPassword = PasswordField('Current password', validators=[InputRequired(), Length(min=6)])
    newPassword1 = PasswordField('New password', validators=[InputRequired(), EqualTo('newPassword2', message="New Passwords must match")])
    newPassword2 = PasswordField('Repeat password')
