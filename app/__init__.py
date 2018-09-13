from flask import Flask, render_template, redirect, url_for, session, flash, logging, request
from flask_mysqldb import MySQL
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config')

mail = Mail(app)
mysql = MySQL(app)

from app.users.controllers import mod_users
from app.articles.controllers import mod_articles
from app.admin.controllers import mod_admin

app.register_blueprint(mod_users)
app.register_blueprint(mod_articles)
app.register_blueprint(mod_admin)
