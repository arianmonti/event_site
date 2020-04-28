import click
#import MySQLdb as mysql
import MySQLdb as mysql
from flask import g
from flask.cli import with_appcontext
from app import config

def connect_db():
    db = mysql.connect(user=config.MYSQL_USERNAME,
                       passwd=config.MYSQL_PASSWORD,
                       host=config.MYSQL_HOST,
                       db=config.MYSQL_DATABASE,
                       charset='utf8'
                        )
    return db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""DROP TABLE IF EXISTS user;""")
    cursor.execute("""
        CREATE TABLE user (
            id INT,
            username VARCHAR(128) PRIMARY KEY,
            first_name VARCHAR(64),
            sur_name VARCHAR(64),
            email VARCHAR(128),
            password VARCHAR(128));
        """)
    
    
    cursor.execute("""DROP TABLE IF EXISTS event;""")
    cursor.execute("""
        CREATE TABLE event (
            id INT,
            title VARCHAR(500),
            description VARCHAR(1000),
            place VARCHAR(2800),
            timestamp DATE DEFAULT CURRENT_DATE,
            time DATE,
            price INT,
            username VARCHAR(128),
            FOREIGN KEY (username) REFERENCES user(username));
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

     
           
