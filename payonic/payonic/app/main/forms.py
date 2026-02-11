from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, SelectMultipleField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

class SplitBillForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    total_amount = FloatField('Total Amount to Split (LKR)', validators=[DataRequired()])
    # In a real app, users would be dynamic. For MVP, we might use a text field or simple select.
    # We'll select users in the route or use a simple string of usernames for now.
    participants = StringField('Participants (comma separated usernames)', validators=[DataRequired()])
    submit = SubmitField('Create Request')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number')
    profile_pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Update Profile')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')
