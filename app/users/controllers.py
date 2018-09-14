from flask import Flask, Blueprint, make_response, render_template, redirect, url_for, session, flash, logging, request
from app import app, mysql, mail
from myfuncs import errors, mylogin, confirm_token, send_email, categories, get_username, get_permissions
from app.decorators import login_required, not_login, confirm_required, admin, has_permission
from passlib.hash import sha256_crypt
from passlib.utils import getrandstr
from app.users.forms import RegisterForm, LoginForm
import random
string = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

mod_users = Blueprint('users', __name__)


@app.route('/')
def index():
    user = session.get('user', '')
    if user:
        permissions=get_permissions(user['id'])
    else:
        permissions = []
    return render_template('index.html', permissions = permissions)

@mod_users.route('/register', methods=['GET', 'POST'])
@not_login
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        username = form.username.data
        name = form.name.data
        password = sha256_crypt.encrypt(form.password.data)
        error = errors(username,email)
        if not error['username'] and not error['email']:
            cursor = mysql.connection.cursor()
            token = getrandstr(random,string,50)
            query = 'insert into users(email, username, name, password, confirmed) VALUES(%s,%s,%s,%s,%s)'
            cursor.execute(query,(email,username,name,password,token))
            mysql.connection.commit()
            cursor.close()
            confirm_url = url_for('users.confirm_email', token=token, _external = True)
            html = render_template('email.html', confirm_url=confirm_url)
            subject = 'Hesabınızı Təsdiqləyin'
            send_email(to = email,subject=subject,template= html)
            flash('Qeydiyyatdan uğurla keçdiniz!','success')
            return redirect(url_for('users.login'))
        elif error['username'] == True:
            flash('Belə istifadəçi adı var','danger')
        elif error['email'] == True:
             flash('Bu email istifadə olunub','danger')
       
    return render_template('users/register.html', form=form)

@mod_users.route('/confirm/<token>')
@login_required
def confirm_email(token):
    status = confirm_token(token, session['user']['id'])
    if status:
        cursor = mysql.connection.cursor()
        cursor.execute('update users set confirmed = 1 where id = %s',(session['user']['id'],))
        mysql.connection.commit()
        flash('Hesabınız Təsdiqləndi. Təşəkkürlər!','success')
        cursor.close()
    else:
        flash('Hesabınız Təsdiqlənib və ya səhv var','danger')
    return redirect(url_for('index'))

@mod_users.route('/activate')
@login_required
def activate():
    cursor = mysql.connection.cursor()
    cursor.execute('select confirmed from users where id = %s', (session['user']['id'],))
    user = cursor.fetchone()
    cursor.close()
    if user['confirmed'] =='1':
        confirmed = True
    else:
        confirmed = False
    return render_template('users/activate.html', confirmed = confirmed)

@mod_users.route('/resend')
@login_required
def resend():
    cursor = mysql.connection.cursor()
    id = session['user']['id']
    cursor.execute('select confirmed,email from users where id =%s',(id,))
    user = cursor.fetchone()
    email = user['email']
    if user['confirmed'] == '1':
        pass
    else:
        token = getrandstr(random, string, 50)
        cursor.execute('update users set confirmed =%s where id=%s',(token,id))
        mysql.connection.commit()
        cursor.close()
        confirm_url = url_for('users.confirm_email', token=token, _external = True)
        html = render_template('email.html', confirm_url=confirm_url)
        subject = 'Hesabınızı Təsdiqləyin'
        send_email(to = email,subject=subject,template= html)
        flash('Yenidən göndərildi','success')
    return redirect(url_for('users.activate'))


@mod_users.route('/login', methods=['GET','POST'])
@not_login
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        email = form.email.data
        raw_password = form.password.data
        status = mylogin(email, raw_password)
        if status == 'success':
            flash('Uğurla daxil oldunuz','success')
            if request.args.get('next', '') == '':
                return redirect(url_for('index'))

            else:
                return redirect(request.args.get('next'))
        elif status == 'wrongemail':
            flash('Belə istifadəçi yoxdur','danger')
            return redirect(url_for('login'))
        elif status == 'wrongpassword':
            flash('Parol Səhvdir','danger')
            return redirect(url_for('login'))
    return render_template('users/login.html', form = form)

@mod_users.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@mod_users.route('/dashboard')
@login_required
def dashboard():
    cursor = mysql.connection.cursor()
    query = 'select * from articles where author = %s order by created_at desc'
    result = cursor.execute(query,(session['user']['id'],))
    if result > 0:
        articles = cursor.fetchall()
    else:
        articles = False
    cursor.close()
    return render_template('users/dashboard.html', articles = articles, permissions = get_permissions(session['user']['id']))

@mod_users.route('/profile/<int:id>')
@login_required
def profile(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute('select * from users where id = %s', (id,))
    if result == 1:
        user = cursor.fetchone()
        result = cursor.execute('select title,id,readtime from articles where author = %s order by created_at desc',(id,))
        if result > 0:
            articles = cursor.fetchall()
        else:
            articles = False
    else:
        flash('Belə istifadəçi yoxdur','danger')
        return redirect(url_for('index'))

    return render_template('users/profile.html', articles= articles, user=user, permissions=get_permissions(session['user']['id']))