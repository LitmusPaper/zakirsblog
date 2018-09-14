from flask import Flask, Blueprint, make_response, render_template, redirect, url_for, session, flash, logging, request
from app import app, mysql, mail
from myfuncs import get_username, get_permissions, change_permission
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
    form = AddPermissonForm(request.form)
    if request.method == 'POST' and form.validate():
        codename = form.codename.data
        name = form.name.data
        form = AddPermissonForm()
        cursor.execute('insert into permissions(codename, name) values(%s,%s)',(codename,name))
        mysql.connection.commit()
    return render_template('admin/addpermission.html', form=form, permissions = get_permissions(session['user']['id']))
@mod_admin.route('/user/edit/<int:id>')
@login_required
@admin
def edituser(id):
    cursor= mysql.connection.cursor()
    result = cursor.execute('select * from users where id =%s',(id,))
    permission = request.args.get('permission','')
    
    if result ==1:
        if permission:
            permission = int(permission)
            message = change_permission(permission,id)
            flash(message,'success')
            return redirect(url_for('admin.edituser', id=id))
        user= cursor.fetchone()
        cursor.execute('select * from permissions')
        permissions = cursor.fetchall()
        userperms = get_permissions(user['id'])
        return render_template('admin/edituser.html',permissions=get_permissions(session['user']['id']), user=user, basepermissions=permissions, userperms=userperms)
    else:
        return redirect(url_for('admin.adminview'))


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
