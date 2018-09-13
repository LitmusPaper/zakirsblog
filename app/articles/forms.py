from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators


class ArticleForm(Form):
    title = StringField('Başlıq:', validators=[
        validators.DataRequired(message="Başlıq mütləq yazılmalıdır"),
        validators.Length(min=5, max=100, message='Başlıq min. 5 maks. 100 simvol ola bilər' )
    ])
    content = TextAreaField("Məqalə:",validators=[
        validators.Length(min=10,message='Məqalə min. 10 simvol olmalıdır')
    ])
    category = SelectField('Kateqoriya:', choices=[])
