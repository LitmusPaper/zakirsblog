from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators


class AddPermissonForm(Form):
    user = StringField('istifadəçinin emaili:', validators=[
        validators.DataRequired(message='Mütləq yazılmalıdır')
    ])
    permission = SelectField('Hansı icazə:', coerce=int, validators=[
        validators.DataRequired(message='mütləq seçilməlidir')
    ])
