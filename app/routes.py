from flask import (
    redirect,
    flash,
    render_template,
    session,
    request,
    url_for
)

from app import app

from app.forms import LoginForm

from werkzeug.security import generate_password_hash, check_password_hash

from app.db import connect_db


@app.route('/index')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user %s' %(form.username.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)