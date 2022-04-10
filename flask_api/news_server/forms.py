from ast import Pass
from django.forms import ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from news_server.models import User


class RegisterForm(FlaskForm):

    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    username      = StringField(label='Username', validators=[Length(min=2,max=30), DataRequired()])
    email_address = StringField(label='Email Address', validators=[Email(), DataRequired()])
    password1     = PasswordField(label='Password', validators=[Length(min=4), DataRequired()])
    password2     = PasswordField(label='Confirm Password', validators=[EqualTo('password1'), DataRequired()])
    submit        = SubmitField(label='Register')

class LoginForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit   = SubmitField(label='Sign In')
