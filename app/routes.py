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

## from app.forms import LoginForm, RegistrationForm

from werkzeug.security import generate_password_hash, check_password_hash

from app.db import connect_db

from flask_login import login_required, current_user, login_user, logout_user, UserMixin, LoginManager


#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_view = "login"
#login_manager.login_message_category = 'danger'


#db = connect_db()
#cur = db.cursor()
#user_id = cur.execute('')





@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = connect_db()
        cursor = db.cursor()
        error = None
        qo = """
            INSERT INTO user (username, password)
            VALUES (%s, %s)
        """
        vo = (username, generate_password_hash(password))
        ql = 'SELECT id FROM user WHERE username = (%s)'
        vl = (username)
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif cursor.execute(ql, vl) is not None:
            error = "You can't user %s username :)" %(username)
        
        if error is None:
            cursor.execute(qo, vo) 
            db.commit()
            return redirect('/')

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
            session['user_id'] = user[1]
            #session['logged_in'] = True
            #login_user(user[1], remember=True)
            #flash('error')
            return redirect(url_for('index'))
    return render_template('login.html')

#@login_manager.user_loader
#def load_user(session):
 #  return session['user_id']
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

@app.route('/index')
@app.route('/')
@login_required
def index():
    try:
        flash(session['user_id'])
    except:
        return redirect('/login')
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



