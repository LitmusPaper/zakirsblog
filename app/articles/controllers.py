from flask import Flask, Blueprint, jsonify, make_response, render_template, redirect, url_for, session, flash, logging, request
from app import app, mysql, mail
from myfuncs import categories, get_username, permisson, get_permissions
from app.decorators import login_required, not_login, confirm_required, admin, has_permission
from app.articles.forms import ArticleForm
import json

mod_articles = Blueprint('articles',__name__)


@mod_articles.route('/delete/<int:id>')
@login_required
@confirm_required
def delete(id):
    cursor = mysql.connection.cursor()
    query = 'select * from articles where id = %s'
    result = cursor.execute(query,(id,))
    if result == 1:
        article = cursor.fetchone()
        if article['author'] == session['user']['id'] or permisson('delete_article'):
            query = 'delete from articles where id = %s'
            cursor.execute(query,(id,))
            mysql.connection.commit()
            cursor.close()
            flash('Məqalə silindi','success')
        else:
            flash('Məqaləni silə bilmərsiz','danger')
    else:
        flash('Belə Məqalə yoxdur','danger')
    return redirect(url_for('index'))

@mod_articles.route('/search', methods=['GET','POST'])
def search():
    key = request.args.get('term')
    cursor = mysql.connect.cursor()
    query = "select * from articles where title like '%{key}%' ".format(key=key)
    result = cursor.execute(query)
    if result > 0:
        articles = cursor.fetchall()
    else:
        articles = []
    result = []
    for article in articles:
        result.append({'label':article['title'],'id':article['id']})
    return json.dumps(result)


@mod_articles.route('/articles')
def articles():
    user = session.get('user', '')
    if user:
        permissions=get_permissions(user['id'])
    else:
        permissions = []
    key = request.args.get('key', False)
    cursor = mysql.connection.cursor()
    if key:
        query = "select * from articles where title like '%{key}%' order by created_at desc".format(key=key)
    else:
        query = 'select * from articles order by created_at desc'
    result = cursor.execute(query)
    if result >0:
        articles = cursor.fetchall()
    else:
        articles = False
    cursor.close()
    return render_template('articles/articles.html', articles = articles, key=key, permissions= permissions)

@mod_articles.route('/article/<int:id>')
def article(id):
    user = session.get('user', '')
    if user:
        permissions=get_permissions(user['id'])
    else:
        permissions = []
    cursor = mysql.connection.cursor()
    query = 'select * from articles where id = %s'
    result = cursor.execute(query,(id,))
    if result == 1:
        article = cursor.fetchone()
        article['author_username'] = get_username(article['author'])
        new_readtime = article['readtime'] + 1
        query = 'update articles set readtime=%s where id = %s'
        cursor.execute(query, (new_readtime,id))
        mysql.connection.commit()
        cursor.close()

    else:
        flash('Belə Məqalə tapılmadı','warning')
        return redirect(url_for('index'))
    return render_template('articles/article.html', article=article, permissions=permissions)

@mod_articles.route('/addarticle', methods=['GET','POST'])
@login_required
@confirm_required
def addarticle():
    form = ArticleForm(request.form)
    form.category.choices = categories()
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['user']['id']
        category = form.category.data
        cursor = mysql.connection.cursor()
        query = 'insert into articles(title, author, content, category) VALUES(%s,%s,%s,%s)'
        cursor.execute(query,(title,author,content,category))
        mysql.connection.commit()
        cursor.close()
        flash('Məqalə Yaradıldı','success')
        return redirect(url_for('users.dashboard'))
    return render_template('articles/addarticle.html', form=form, permissions=get_permissions(session['user']['id']))

@mod_articles.route('/edit/<int:id>', methods = ['GET','POST'])
@login_required
@confirm_required
def edit(id):
    cursor = mysql.connection.cursor()
    query = 'select * from articles where id = %s'
    result = cursor.execute(query,(id,))
    if result == 1:
        article = cursor.fetchone()
        if article['author'] == session['user']['id'] or permisson('edit_article'):
            form = ArticleForm(data=article)
            form.category.choices = categories()
            if request.method == 'POST' and form.validate():
                form = ArticleForm(request.form)
                query = 'update articles set title = %s, content = %s, category = %s where id = %s'
                cursor.execute(query,(form.data['title'], form.data['content'], form.data['category'], id ))
                mysql.connection.commit()
                cursor.close()
                flash('Məqalə Dəyişdirildi','success')
                return redirect(url_for('users.dashboard'))
        else:
            flash('Bu məqaləni redaktə edə bilmərsiz','danger')
            return redirect(url_for('users.dashboard'))
    else:
        flash('Belə məqaləniz yoxdur','danger')
        return redirect(url_for('users.dashboard'))
    return render_template('articles/edit.html', form=form,article=article, permissions=get_permissions(session['user']['id']))
