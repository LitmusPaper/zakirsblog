from functools import wraps
from flask import request, redirect, url_for, session, flash
from app import app, mysql



def has_permission(permission, **kwargs):  
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cursor=mysql.connection.cursor()
            result=cursor.execute('select users_permissions.*, permissions.id \
            from users_permissions\
            join permissions on permissions.id = users_permissions.permission_id\
            where permissions.codename = %s and users_permissions.user_id = %s \
            ',(permission,session['user']['id']))
            cursor.close()
            if result >0:
                return func(*args, **kwargs)
            else:
                flash('Buna icazəniz yoxdur!','danger')
                return redirect(url_for('index'))
        return wrapper
    return decorator

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            cursor = mysql.connection.cursor()
            result = cursor.execute('select * from users where id = %s', (session['user']['id'],))
            cursor.close()
            if result == 1:
                return f(*args, **kwargs)
            else:
                session.clear()
                return redirect(url_for('index'))
            
        else:
            flash('Daxil olmalısız','warning')
            return redirect(url_for('users.login', next=request.url))
        
    return decorated_function

def confirm_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cursor = mysql.connection.cursor()
        cursor.execute('select confirmed from users where id = %s', (session['user']['id'],))
        user = cursor.fetchone()
        cursor.close()
        if user['confirmed'] == '1':
            return f(*args, **kwargs)
        else:
            return redirect(url_for('users.activate'))
        
    return decorated_function

def not_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return redirect(url_for('index'))
        else:
            return f(*args, **kwargs)
    return decorated_function

def admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cursor = mysql.connection.cursor()
        cursor.execute('select superuser from users where id =%s',(session['user']['id'],))
        user=cursor.fetchone()
        cursor.close()
        if user['superuser']:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('index'))
        
        
    return decorated_function