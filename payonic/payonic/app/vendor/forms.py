from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class BankDetailsForm(FlaskForm):
    bank_name = StringField('Bank Name', validators=[DataRequired(), Length(max=100)])
    account_number = StringField('Account Number', validators=[DataRequired(), Length(max=50)])
    account_holder_name = StringField('Account Holder Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Bank Details')

class PayoutRequestForm(FlaskForm):
    amount = FloatField('Claim Amount (LKR)', validators=[DataRequired(), NumberRange(min=100.0, message="Minimum claim is LKR 100")])
    submit = SubmitField('Submit Claim Request')
