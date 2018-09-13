from flask import Flask, render_template, redirect, url_for, session, flash, logging, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from flask_mail import Mail, Message
from app import mysql, mail

def get_permissions(id):
    cursor = mysql.connection.cursor()
    cursor.execute('\
    SELECT permissions.codename, permissions.name\
    FROM permissions\
    JOIN users_permissions ON permissions.id = users_permissions.permission_id\
    where users_permissions.user_id = %s', (id,))
    tup = cursor.fetchall()
    cursor.close()
    permissions = []
    for permission in tup:
        permissions.append(permission['codename'])
    return permissions

def permisson(permission):
    cursor=mysql.connection.cursor()
    result=cursor.execute('select users_permissions.*, permissions.id \
    from users_permissions\
    join permissions on permissions.id = users_permissions.permission_id\
    where permissions.codename = %s and users_permissions.user_id = %s \
    ',(permission,session['user']['id']))
    cursor.close()
    if result >0:
        return True
    else:
        return False

def get_username(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute('select username from users where id = %s',(id,))
    if result ==1:
        user = cursor.fetchone()
        username = user['username']
    else:
        username = 'Deleted User'
    return username

def categories():
    cursor = mysql.connection.cursor()
    cursor.execute('select * from categories')
    categories = cursor.fetchall()
    cursor.close()
    choices = []
    for category in categories:
        choices.append((category['name'], category['name']))
    return choices

def send_email(to, subject, template):
    msg = Message(subject, recipients=[to], html=template)
    mail.send(msg)

def errors(username,email):
    errors = {'username':False, 'email':False}
    cursor = mysql.connection.cursor()
    result = cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    result2 = cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

    if result != 0:
        errors['username'] = True
    else:
        pass
    if result2 != 0:
        errors['email'] = True
    else:
        pass
    cursor.close()
    return errors

def mylogin(email, raw_password):
    cursor = mysql.connection.cursor()
    result =  cursor.execute("select * from users where email = %s",(email,))

    if result == 1:
        data = cursor.fetchone()
        cursor.close()
        real_password = data['password']
        if sha256_crypt.verify(raw_password, real_password):
            session['logged_in'] = True
            session['user'] = {
                'id':data['id'],
                'username': data['username'],
                'name':data['name'],
                'email':data['email'],
                'is_superuser':data['superuser']
            }
            return 'success'
        else:
            return 'wrongpassword'
    else:
        return 'wrongemail'


def confirm_token(token, id):
    cursor = mysql.connection.cursor()
    result = cursor.execute('select confirmed from users where id= %s',(id,))
    if result == 1:
        user = cursor.fetchone()
        usertoken = user['confirmed']
        cursor.close()
        if usertoken == '1':
            return False
        elif usertoken == token:
            return True
        else:
            return False
    else:
        return False

