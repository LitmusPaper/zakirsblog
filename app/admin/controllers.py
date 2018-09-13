from flask import Flask, Blueprint, make_response, render_template, redirect, url_for, session, flash, logging, request
from app import app, mysql, mail
from myfuncs import errors, mylogin, confirm_token, send_email, categories, get_username, get_permissions
from app.decorators import login_required, not_login, confirm_required, admin, has_permission
from app.admin.forms import AddPermissonForm

mod_admin = Blueprint('admin',__name__)



@mod_admin.route('/admin')
@login_required
@has_permission('view_panel')
def adminview():
    cursor = mysql.connection.cursor()
    cursor.execute('select * from articles order by created_at desc limit 5')
    articles = cursor.fetchall()
    cursor.execute('select id,username,email,confirmed from users order by id desc limit 5')
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin/admin.html', users=users, articles=articles, permissions = get_permissions(session['user']['id']))
    
@mod_admin.route('/addpermission', methods = ['GET', 'POST'])
@login_required
@admin
def addpermission():
    cursor = mysql.connection.cursor()
    cursor.execute('select id, name from permissions')
    tuppermissions = cursor.fetchall()
    permissions = []
    for permission in tuppermissions:
        permissions.append((permission['id'],permission['name']))
    form = AddPermissonForm(request.form)
    form.permission.choices = permissions
    if request.method == 'POST' and form.validate():
        email = form.user.data
        permission = form.permission.data
        result = cursor.execute('select id from users where email = %s',(email,))
        if result == 1:
            user = cursor.fetchone()
            userid = user['id']
            result = cursor.execute('select * from users_permissions where user_id = %s and permission_id = %s',(userid,permission))
            if result == 0:
                cursor.execute('insert into users_permissions(permission_id, user_id) VALUES(%s,%s)',(permission,userid))
                mysql.connection.commit()
                flash('İstifadəçiyə icazə verildi!','success')
            else:
                flash('bu istifadəçinin artıq buna icazəsi var','danger')
        else:
            flash('belə istifadəçi yoxdur','danger')
        cursor.close()
    return render_template('admin/addpermission.html', form=form, permissions = get_permissions(session['user']['id']))

@mod_admin.route('/admin/users')
@login_required
@has_permission('view_panel')
def users():
    cursor = mysql.connection.cursor()
    key = request.args.get('key','')
    if key:
        cursor.execute("select id,username,email,confirmed from users\
         where username like '%{key}%' or email like '%{key}%' order by id desc".format(key=key))
    else:
        cursor.execute('select id,username,email,confirmed from users order by id desc')
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin/users.html', key=key, users = users, permissions=get_permissions(session['user']['id']))

@mod_admin.route('/user/delete/<int:id>')
@login_required
@has_permission('delete_user')
def deleteuser(id):
    cursor = mysql.connection.cursor()
    result = cursor.execute('select id from users where id = %s', (id,))
    if result == 1:
        cursor.execute('delete from users where id = %s', (id,))
        cursor.execute('delete from users_permissions where user_id = %s', (id,))
        mysql.connection.commit()
        flash('istifadəçi silindi','success')
    else:
        flash('Belə istifadəçi yoxdur','danger')
    return redirect(url_for('admin.users'))
