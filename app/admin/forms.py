from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators


class AddPermissonForm(Form):
    codename = StringField('codename:', validators=[
        validators.DataRequired(message='Mütləq yazılmalıdır')
    ])
    name = StringField('name:', validators=[
        validators.DataRequired(message='mütləq seçilməlidir')
    ])
 