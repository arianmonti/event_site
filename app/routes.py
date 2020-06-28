""" All app routes on Freevent
"""

from hashlib import md5
from functools import wraps
import os
import redis
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user
from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from app import app
from app import config
from app.db import connect_db

r = redis.Redis(host='localhost', port=6379, db=0)  # Connect to Redis

def get_redis(username):
    ''' Get redis username and return it. Unnecessary '''
    result = r.get(username)
    return result


def avatar(username, size):
    '''Get avatar from Gravatar'''
    digest = md5(username.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
        digest, size)

@app.before_request
def before_request():
    ''' Defines some data before requests '''
    g.user = current_user


def login_required(function):
    ''' Define login required function. I didn't use Flask_Login '''
    @wraps(function)
    def decorated_function(*args, **kwargs):
        try:
            session['username']
        except KeyError:
            return redirect('/login')
        return function(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    ''' Registers users and redirects to Login Page '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        email = request.form['email']
        database = connect_db()
        cursor = database.cursor()
        error = None
        first_query = """
            INSERT INTO user
                (username, email, password)
                VALUES (%s, %s, %s)
        """
        first_value = (username, email, generate_password_hash(password))
        secound_query = 'SELECT username FROM user WHERE username = (%s)'
        secound_value = (username,)

        cursor.execute(secound_query, secound_value)
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif cursor.fetchone() is not None:
            error = "You can't use user %s username :)" % (username)
        elif password != repeat_password:
            error = "passwords don't math."
        if error is None:
            cursor.execute(first_query, first_value)
            r.set('%s' % username, '%s' % avatar(username, 80))
            database.commit()
            return redirect('/login')

        flash(error)
    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    ''' Login registered users and redirect to User Page '''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = connect_db()
        cur = database.cursor()
        error = None
        cur.execute("SELECT * FROM user WHERE username = (%s)", (username,))
        user = cur.fetchone()
        database.commit()
        if user is None:
            error = 'Incorrect username.'
            flash(error)
        elif not check_password_hash(user[3], password):
            error = 'Incorrect password.'
            flash(error)
        if error is None:
            session.clear()
            session['username'] = user[1]
            username = session['username']
            return redirect('/user/%s' % (username))

    return render_template('login.html')

@app.route('/index')
@app.route('/')
def index():
    ''' Index Page '''
    try:
        username = session['username']
        return redirect('/user/%s' % (username))
    except KeyError:
        pass
    return render_template('base.html')


@app.route('/logout')
def logout():
    ''' Logs out '''
    session.clear()
    return redirect(url_for('index'))


@app.route('/user/<username>')
@login_required
def user_profile(username):
    ''' User Page shows profile and evnets '''
    if username != session['username']:
        return redirect('/login')
    database = connect_db()
    cursor = database.cursor()

    cursor.execute("""
            SELECT  title, description,
                    place, timestamp,
                    time, price, username
                    FROM event
            """)
    posts = cursor.fetchall()
    user_avatar = avatar(username, 128)
    return render_template(
        'user.html',
        user=session['username'],
        posts=posts,
        avatar=avatar,
        get_redis=get_redis,
        user_avatar=user_avatar)


@app.route('/user/<username>/new_event', methods=['GET', 'POST'])
@login_required
def new(username):
    ''' Creates new Event Post for user '''
    if username != session['username']:
        return redirect('/login')
    if request.method == 'POST':
        error = None
        user = session['username']
        title = request.form['title']
        description = request.form['description']
        place = request.form['place']
        time = request.form['time']
        price = request.form['price']
        data = [title, place, time, price]
        database = connect_db()
        cur = database.cursor()
        if len(price) > 7:
            error="This event is too expensive"
        if len(description) > 80:
            error="Too long description"
        if error is None:
            first_query = """
                INSERT INTO event
                    (title, description, place, time, price, username)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
            first_value = (
                title,
                description,
                place,
                time,
                int(price),
                session['username'])
            cur.execute(first_query, first_value)
            database.commit()

            return redirect('/user/%s' % (user))
        flash(error)
    return render_template('new.html', username=username)


def allowed_file(filename):
    ''' Normalization file name for upload in profile'''
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/user/<username>/new_profile', methods=['GET', 'POST'])
@login_required
def upload_file(username):
    ''' Uploads new profile image '''
    if username != session['username']:
        return redirect('/login')
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            r.set('%s' % username, '/static/images/%s' % filename)
            return redirect('/user/%s' % (username))
    return render_template('upload.html', username=username)


@app.route('/user/<username>/remove_profile')
@login_required
def remove_profile(username):
    ''' Removes profile image and choose Gravatar for Profile '''
    if username != session['username']:
        return redirect('/login')
    r.set('%s' % username, '%s' % avatar(username, 80))
    return redirect('/user/%s' % (username))
