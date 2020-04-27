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
        #first_name = request.form['first_name']
        #last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
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
        elif password != repeat_password:
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
        elif not check_password_hash(user[5], password):
            error = 'Incorrect password.'
            flash(error)
        if error is None:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[4]
            username = session['username']
            return redirect('/user/%s'%(username))

    return render_template('login.html')

@app.before_request
def before_request():
    g.user = current_user

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            username = session['username']
        except:
            return redirect('/login')
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
    return render_template('base.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/<username>')
@login_required
def user(username):
    user =  session['username']
    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT  title, description, place, timestamp, time, price, author_username FROM event""")

    posts = cursor.fetchall()
    return render_template('user.html', posts=posts ,user=user)

@app.route('/user/<username>/new_event', methods=['GET', 'POST'])
@login_required
def new(username):
    if request.method ==  'POST':
        user = session['username']
        title = request.form['title']
        description = request.form['description']
        place = request.form['place']
        time = request.form['time']
        price = request.form['price']
        #flash(session['username']) 
        error = None 
        data = [title, place, time, price]
        db = connect_db()
        cur = db.cursor()
        for d in data:
            if data == None:
                error = 'Fill out all!!'
        if error is None:
            qo = """INSERT INTO event (title, description, place, time, price, author_username) VALUES (%s, %s, %s, %s, %s, %s)"""
            vo = (title, description, place, time, price, session['username'])
            cur.execute(qo, vo)
            db.commit()
            return redirect('/user/%s' %(user) )
            #flash(session['username'])
        flash(error)
    return render_template('new.html')

