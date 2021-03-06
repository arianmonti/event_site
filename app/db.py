from flask import g
from app import config
from flask.cli import with_appcontext
import MySQLdb as mysql
import click

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
    '''Delete old same tables and create new tables'''
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("""DROP TABLE IF EXISTS user;""")
    cursor.execute("""
        CREATE TABLE user (
            id                  INT,
            username            VARCHAR(128)        PRIMARY KEY,
            email               VARCHAR(128),
            password            VARCHAR(128)        CHARACTER SET utf8mb4 COLLATE UTF8MB4_UNICODE_CI
            );
        """)

    cursor.execute("""DROP TABLE IF EXISTS event;""")
    cursor.execute("""
        CREATE TABLE event (
            id                  INT,
            title               VARCHAR(80)        CHARACTER SET utf8mb4 COLLATE UTF8MB4_UNICODE_CI,
            description         VARCHAR(80)         CHARACTER SET utf8mb4 COLLATE UTF8MB4_UNICODE_CI,
            place               VARCHAR(80)       CHARACTER SET utf8mb4 COLLATE UTF8MB4_UNICODE_CI,
            timestamp           DATE                DEFAULT CURRENT_DATE,
            time                DATE,
            price               INT,
            username            VARCHAR(64)
            )
        ;""")

# TODO Add type
# TODO Add subject
# TODO file


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Create CLI app'''
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
