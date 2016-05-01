# coding: utf-8
from flask import Flask
from flask import render_template
from flask import request,redirect,flash,get_flashed_messages,url_for,escape
from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config["SECRET_KEY"] = "KOZHEDED"
app.config["REMEMBER_COOKIE_DURATION"] = datetime.timedelta(minutes=30)


engine = create_engine('sqlite:///kozheded.db',pool_recycle=3600, encoding="utf-8")
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


class Joke(Base):
    __tablename__ = 'jokes'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    timestamp = Column(DateTime)

    def __init__(self, text):
        self.text = text
        self.timestamp = datetime.datetime.now()

def init_db():
    Base.metadata.create_all(bind=engine)
    joke = Joke(u'Когда я умер, не было никого, кто бы не засмеялся!')
    db_session.add(joke)
    db_session.commit()


@app.route('/')
def index():
    jokes = Joke.query.order_by('timestamp desc')
    return render_template('index.html', jokes=jokes)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'GET':
        return render_template('add.html')
    if request.method == 'POST':
        text = escape(request.form['text'])
        timestamp = datetime.datetime.now()
        if len(text) > 0:
            joke = Joke(text)
            db_session.add(joke)
            db_session.commit()
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
