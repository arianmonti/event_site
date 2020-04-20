from flask import (
    redirect,
    flash,
    g,
    render_template,
    session,
    request,
    url_for
)

from functools import wraps

from app import app

from werkzeug.security import generate_password_hash, check_password_hash

from app.db import connect_db

from hashlib import md5

from flask_login import login_required, current_user

from markupsafe import escape

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repet_password = request.form['repet_password']
        email = request.form['email']
        db = connect_db()
        cursor = db.cursor()
        error = None
        qo = """
            INSERT INTO user (username, email, password)
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
           error = "You can't user user %s username :)" %(username)
        elif password != repet_password:
            error = "passwords don't math."
        
        if error is None:
            cursor.execute(qo, vo) 
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
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            username = session['username']
            return redirect('/user/%s'%(username))

    return render_template('login.html')

@app.before_request
def before_request():
    g.user = current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/index', methods=['GET, POST'])
@app.route('/')
def index():
    try:
        username = session['username']
        return(redirect('/user/%s' %(username)))
    except:
        pass
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    try:
        user =  session['username']

    except:
        return redirect('/login')
    return render_template('user.html', user=user)
