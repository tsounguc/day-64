import os

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, VARCHAR, String, Float
from sqlalchemy.orm import Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

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

api_key = os.environ.get("api_key", "Couldn't find api_key")
token = os.environ.get("token", "Couldn't find token")
url = "https://api.themoviedb.org/3/search/movie"


class RatingForm(FlaskForm):
    rating = StringField(label='Your Rating Out of 10 e.g 7.5', validators=[DataRequired(), ])
    review = StringField(label='Your Review', validators=[DataRequired()])
    done = SubmitField('Done')


class AddMovieForm(FlaskForm):
    title = StringField(label='Movie Title', validators=[DataRequired()])
    add = SubmitField('Add Movie')


class Movies(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=False)
    year: Mapped[str] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(VARCHAR, nullable=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    with app.app_context():
        # get movie list from lowest rating to highest
        movie_list = db.session.execute(db.select(Movies).order_by(Movies.rating)).scalars().all()

        # reverse so the highest rating is the first item and lowest is last on the list
        movie_list.reverse()

        # update ranking based on rating
        for index in range(0, len(movie_list)):
            book_to_update = db.session.execute(db.select(Movies).where(Movies.id == movie_list[index].id)).scalar()
            book_to_update.ranking = index + 1
            db.session.commit()

        # get updated movie list
        movie_list = db.session.execute(db.select(Movies).order_by(Movies.ranking)).scalars().all()
        
    return render_template("index.html", movies=movie_list)


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        print(movie_title)
        end_point = f"{url}?query={movie_title}&api_key={api_key}"
        # headers = {
        #     "accept": "application/json",
        #     "Authorization": f"Bearer {token}"
        # }

        response = requests.get(end_point)
        response.raise_for_status()
        movies_data = response.json()
        print(movies_data)

        return render_template("select.html", movies=movies_data['results'])
    return render_template("add.html", form=form)


@app.route("/edit/<int:movie_id>", methods=['GET', 'POST'])
def edit(movie_id):
    form = RatingForm()
    with app.app_context():
        movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
    if form.validate_on_submit():
        with app.app_context():
            movie_to_update = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
            movie_to_update.rating = form.rating.data
            movie_to_update.review = form.review.data
            db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", title=movie_to_update.title, form=form)


@app.route('/select/<int:movie_id>')
def select(movie_id):
    movie_details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(url=movie_details_url, headers=headers)
    response.raise_for_status()
    data = response.json()
    print(data)

    with app.app_context():
        movie_to_add = Movies(
            title=data['title'],
            img_url=f"https://image.tmdb.org/t/p/original/{data['poster_path']}",
            year=data['release_date'],
            description=data['overview'],
            rating=0.0,
            ranking="",
            review=""

        )
        db.session.add(movie_to_add)
        db.session.commit()

        movie_to_edit = db.session.execute(db.select(Movies).where(Movies.title == data['title'])).scalar()
    return redirect(url_for('edit', movie_id=movie_to_edit.id))


@app.route('/delete/<int:movie_id>')
def delete(movie_id):
    with app.app_context():
        movie_to_delete = db.session.execute(db.select(Movies).where(Movies.id == movie_id)).scalar()
        db.session.delete(movie_to_delete)
        db.session.commit()
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
