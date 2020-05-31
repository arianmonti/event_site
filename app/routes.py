from app import app
from app.db import connect_db
from flask import (
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from app import config
from flask_login import current_user
from functools import wraps
from hashlib import md5
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import redis


r = redis.Redis(host='localhost', port=6379, db=0)  # Connect to Redis


def get_redis(username):
    result = r.get(username)
    return result


def avatar(username, size):
    '''Get avatar from Gravatar'''
    digest = md5(username.lower().encode('utf-8')).hexdigest()
    return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
        digest, size)


@app.before_request
def before_request():
    g.user = current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            session['username']
        except BaseException:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        email = request.form['email']
        db = connect_db()
        cursor = db.cursor()
        error = None
        qo = """
            INSERT INTO user
                (username, email, password)
                VALUES (%s, %s, %s)
        """
        vo = (username, email, generate_password_hash(password))
        ql = 'SELECT username FROM user WHERE username = (%s)'
        vl = (username,)

        cursor.execute(ql, vl)
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif cursor.fetchone() is not None:
            error = "You can't use user %s username :)" % (username)
        elif password != repeat_password:
            error = "passwords don't math."
        if error is None:
            cursor.execute(qo, vo)
            r.set('%s' % username, '%s' % avatar(username, 80))
            db.commit()
            return redirect('/login')

        flash(error)
    return render_template('register.html')


@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = connect_db()
        cur = db.cursor()
        error = None
        cur.execute("SELECT * FROM user WHERE username = (%s)", (username,))
        user = cur.fetchone()
        db.commit()
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
    try:
        username = session['username']
        return(redirect('/user/%s' % (username)))
    except BaseException:
        pass
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def check_empty_profile(profile_uli):
    result = os.path.exists('%s' % (profile_uli))
    return result


@app.route('/user/<username>')
@login_required
def user(username):
    user = session['username']
    db = connect_db()
    cursor = db.cursor()

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
        user=user,
        posts=posts,
        avatar=avatar,
        get_redis=get_redis,
        user_avatar=user_avatar,
        check_empty_profile=check_empty_profile)


@app.route('/user/<username>/new_event', methods=['GET', 'POST'])
@login_required
def new(username):
    if request.method == 'POST':
        user = session['username']
        title = request.form['title']
        description = request.form['description']
        place = request.form['place']
        time = request.form['time']
        price = request.form['price']
        error = None
        data = [title, place, time, price]
        db = connect_db()
        cur = db.cursor()
        for d in data:
            if data is None:
                error = 'Fill out all!!'
        if error is None:
            qo = """
                INSERT INTO event
                    (title, description, place, time, price, username)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
            vo = (
                title,
                description,
                place,
                time,
                int(price),
                session['username'])
            cur.execute(qo, vo)
            db.commit()

            return redirect('/user/%s' % (user))
        flash(error)
    return render_template('new.html')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@app.route('/user/<username>/new_profile', methods=['GET', 'POST'])
@login_required
def upload_file(username):
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
    r.set('%s' % username, '%s' % avatar(username, 80))
    return redirect('/user/%s' % (username))
