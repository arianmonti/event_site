import click
import MySQLdb as mysql
from flask import g
from flask.cli import with_appcontext
import app.config as config

def connect_db():
    db = mysql.connect(user=config.MYSQL_USERNAME,
                       passwd=config.MYSQL_PASSWORD,
                       host=config.MYSQL_HOST,
                       db=config.MYSQL_DATABASE
                        )
    return db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = connect_db()
    cursor = db.cursor()
    
    cursor.execute("""
        DROP TABLE IF EXISTS user;
        CREATE TABLE user (
            id INT PRIMARY KEY AUTO_INCREMENT,
            username VARCHAR(128),
            email VARCHAR(128),
            password VARCHAR(128)
            );
    """)
    ##print('user added')
    ##FKRFJFJSRIOEJRER
       
    cursor.execute("""
        DROP TABLE IF EXISTS event;
        CREATE TABLE event (
            id INT,
            title VARCHAR(500),
            description VARCHAR(1000),
            place VARCHAR(2800),
            timestamp DATE DEFAULT CURRENT_DATE,
            time DATE,
            price INT,
            user_id INT,
            FOREIGN KEY (user_id) REFERENCES user(id)
            );
    """)
    ##print('event added')


#TODO Add type
#TODO Add subject
#TODO file

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

     
           
