from wtforms import Form, StringField, TextAreaField, PasswordField, SelectField, validators



class RegisterForm(Form):
    email = StringField('Email:', validators=[
        validators.Email(message='Düzgün email yazın'),
        validators.DataRequired(message='Email mütləq yazılmalıdır')
    ])
    username = StringField('Nickname:', validators=[
        validators.DataRequired(message='Nickname yazmamısız')
    ])
    name = StringField('Ad, Soyad:', validators=[
        validators.DataRequired(message='Ad və soyad yazılmalıdır'),
        validators.Length(min=5,max=25,message='Ad və soyadınızı düzgün yazın')
    ])
    password = PasswordField('Parol:',validators=[
        validators.Length(min=8,message='Parol minimum 8 simvol olmalıdır'),
        validators.EqualTo('confirm', message='Parollar fərqlidi')
    ], description='min. 8 simvol')
    confirm = PasswordField('Parolu Təsdiqlə:', description='Parolu təkrar yazın')

class LoginForm(Form):
    email = StringField('Email:')
    password = PasswordField('Parol:')
