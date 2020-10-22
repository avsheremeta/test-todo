from wtforms import Form, TextAreaField, BooleanField
from wtforms.validators import InputRequired

class TaskForm(Form):
    description = TextAreaField('', validators=[InputRequired()])



