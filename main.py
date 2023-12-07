from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, VARCHAR, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

'''
Red underlines? Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

# create the extension
db = SQLAlchemy()

# create the app
app = Flask(__name__)

# configure secret key
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"

# initialize the app with the extension
db.init_app(app)

Bootstrap5(app)


class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key= True)
    title: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=False)
    year: Mapped[str] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    ranking: Mapped[int] = mapped_column(Integer, nullable=False)
    review: Mapped[str] = mapped_column(String, nullable=False)
    img_url: Mapped[str] = mapped_column(VARCHAR, nullable=False)


with app.app_context():
    db.create_all()

    new_movie = Movies(
        title="Phone Booth",
        year=2002,
        description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=7.3,
        ranking=10,
        review="My favourite character was the caller.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    )



@app.route("/")
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
