from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('student', 'Student'), ('vendor', 'Vendor'), ('admin', 'Admin')])
    submit = SubmitField('Update User')

class RechargeForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    amount = FloatField('Amount (LKR)', validators=[DataRequired()])
    submit = SubmitField('Recharge Wallet')
