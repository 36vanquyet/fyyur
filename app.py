#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY
from flask_migrate import Migrate
from sqlalchemy import literal_column
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import data_sample

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(ARRAY(db.String))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
       return f'<Venue {self.id}, Name {self.name}, City {self.city}, State {self.state},\
                Phone {self.phone}, Genres {self.genres}, Imgage {self.image_link}, Facebook {self.facebook_link},\
                Website {self.website_link}, SeeTalent {self.seeking_talent}, Decription {self.seeking_description}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    genres = db.Column(ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
       return f'<Artist {self.id}, Name {self.name}, City {self.city}, State {self.state}, Phone {self.phone},\
                Genres {self.genres}, Imgage {self.image_link}, Facebook {self.facebook_link}, Website {self.website_link},\
                SeeVenue {self.seeking_venue}, Decription {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
   __tablename__ = 'Shows'

   id = db.Column(db.Integer, primary_key=True)
   venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
   artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'))
   start_time = db.Column(db.TIMESTAMP)

   def __repr__(self):
      return f'<Show {self.id}, Venue {self.venue_id}, Artist {self.artist_id}, Start Time {self.start_time}>'

app.app_context().push()
#To test with data sample then uncomment db.drop_all() and line 601 'insert_data_sample()'
#db.drop_all()
db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
def insert_data_sample():
  # Insert venues sample
  for venue_data in data_sample.venues:
    id = venue_data.get('id')
    query_venue = Venue.query.filter_by(id=id).first()
    if query_venue is not None:
      for key, value in venue_data.items():
        setattr(query_venue, key, value)
    else:
      new_venue = Venue(**venue_data)
      db.session.add(new_venue)
  
  # Insert artists sample
  for artist_data in data_sample.artists:
    id = artist_data.get('id')
    query_artist = Artist.query.filter_by(id=id).first()
    if query_artist is not None:
      for key, value in artist_data.items():
        setattr(query_artist, key, value)
    else:
      new_artist = Artist(**artist_data)
      db.session.add(new_artist)

  # Commit to save the changes to db
  db.session.commit()
  
  # Insert shows sample
  for show_data in data_sample.shows:
    id = show_data.get('id')
    query_show = Shows.query.filter_by(id=id).first()
    if query_show is not None:
      for key, value in show_data.items():
        setattr(query_show, key, value)
    else:
      new_show = Shows(**show_data)
      db.session.add(new_show)
  # Commit to save the changes to db
  db.session.commit()

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  cities_states_with_venues = db.session.query(Venue.city, Venue.state).distinct().all()
  data = []
  for city, state in cities_states_with_venues:
    venues = []
    venues_in_city_state = Venue.query.filter_by(city=city, state=state).with_entities(Venue.id, Venue.name).all()
    for venue in venues_in_city_state:
      count_up = db.session.query(func.count(Shows.id)).filter(Shows.venue_id == venue.id, Shows.start_time > datetime.now()).scalar()
      venues.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": count_up
      })
    data.append({
      "city": city,
      "state": state,
      "venues": venues
    })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data_find = request.form.get("search_term")
  query_results = Venue.query.filter(Venue.name.ilike(f"%{data_find}%")).with_entities(Venue.id, Venue.name).all()
  count = len(query_results)
  venues = []
  for venue in query_results:
    count_up = db.session.query(func.count(Shows.id)).filter(Shows.venue_id == venue.id, Shows.start_time > datetime.now()).scalar()
    venues.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": count_up
    })

  response={
    "count": count,
    "data": venues
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  query_venue = Venue.query.filter_by(id=venue_id).first()
  data = {}
  href = 'pages/show_venue.html'
  if query_venue is not None:
    past_shows_query = db.session.query( Shows.artist_id,
                                   Artist.name.label("artist_name"),
                                   Artist.image_link.label("artist_image_link"),
                                   Shows.start_time)\
    .join(Shows, Shows.artist_id == Artist.id)\
    .filter(Shows.venue_id == venue_id, Shows.start_time < datetime.now()).all()
    past_shows = []
    for show in past_shows_query:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      })

    upcoming_shows_query = db.session.query(Shows.artist_id,
                                      Artist.name.label("artist_name"),
                                      Artist.image_link.label("artist_image_link"),
                                      Shows.start_time)\
    .join(Shows, Shows.artist_id == Artist.id)\
    .filter(Shows.venue_id == venue_id, Shows.start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
      upcoming_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist_name,
        "artist_image_link": show.artist_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      })

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)
    data = {
      "id": query_venue.id,
      "name": query_venue.name,
      "genres": query_venue.genres,
      "address": query_venue.address,
      "city": query_venue.city,
      "state": query_venue.state,
      "phone": query_venue.phone,
      "website": query_venue.website_link,
      "facebook_link": query_venue.facebook_link,
      "seeking_talent": query_venue.seeking_talent,
      "seeking_description": query_venue.seeking_description,
      "image_link": query_venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
    }
  else:
    href = 'errors/404.html'
  
  return render_template(href, venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # I don't known why: here when I add venue but don't use id then error duplicate key
  # So resole this matter. I get id of element last after increase 1.
  last = Venue.query.order_by(Venue.id.desc()).first()
  id = last.id + 1
  new_venue = Venue(id=id,
                    name=request.form.get('name'),
                    city=request.form.get('city'),
                    state=request.form.get('state'),
                    address=request.form.get('address'),
                    phone=request.form.get('phone'),
                    image_link=request.form.get('image_link'),
                    facebook_link=request.form.get('facebook_link'),
                    genres=request.form.getlist('genres'),
                    website_link=request.form.get('website_link'),
                    seeking_talent=bool(request.form.get('seeking_talent')),
                    seeking_description=request.form.get('seeking_description'))
  # TODO: modify data to be the data object returned from db insertion
  try:
    db.session.add(new_venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + new_venue.name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  query_venue = Venue.query.filter_by(id=venue_id).first()
  if query_venue is not None:
    # Search foreign key and delete it, before delete venue
    show_venue = Shows.query.filter_by(venue_id=venue_id).all()
    for show in show_venue:
      db.session.delete(show)
    
    try:
      db.session.delete(query_venue)
      db.session.commit()
      flash('Venue with ID ' + venue_id + ' was successfully deleted!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue could not be deleted.')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.with_entities(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data_find = request.form.get("search_term")
  query_results = Artist.query.filter(Artist.name.ilike(f"%{data_find}%")).with_entities(Artist.id, Artist.name).all()
  count = len(query_results)

  response={
    "count": count,
    "data": query_results
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  query_artist = Artist.query.filter_by(id=artist_id).first()
  data = {}
  href = 'pages/show_artist.html'
  if query_artist is not None:
    past_shows_query = db.session.query(Shows.venue_id,
                                   Venue.name.label("venue_name"),
                                   Venue.image_link.label("venue_image_link"),
                                   Shows.start_time)\
    .join(Shows, Shows.venue_id == Venue.id)\
    .filter(Shows.artist_id == artist_id, Shows.start_time < datetime.now()).all()
    past_shows = []
    for show in past_shows_query:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_name,
        "venue_image_link": show.venue_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      })

    upcoming_shows_query = db.session.query(Shows.venue_id,
                                   Venue.name.label("venue_name"),
                                   Venue.image_link.label("venue_image_link"),
                                   Shows.start_time)\
    .join(Shows, Shows.venue_id == Venue.id)\
    .filter(Shows.artist_id == artist_id, Shows.start_time > datetime.now()).all()
    upcoming_shows = []
    for show in upcoming_shows_query:
      upcoming_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue_name,
        "venue_image_link": show.venue_image_link,
        "start_time": show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
      })

    past_shows_count = len(past_shows)
    upcoming_shows_count = len(upcoming_shows)
    data = {
      "id": query_artist.id,
      "name": query_artist.name,
      "genres": query_artist.genres,
      "city": query_artist.city,
      "state": query_artist.state,
      "phone": query_artist.phone,
      "website": query_artist.website_link,
      "facebook_link": query_artist.facebook_link,
      "seeking_venue": query_artist.seeking_venue,
      "seeking_description": query_artist.seeking_description,
      "image_link": query_artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
    }
  else:
    href = 'errors/404.html'

  return render_template(href, artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).first()

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  search_artist_id = Artist.query.filter_by(id=artist_id).first()

  if search_artist_id is not None:
    search_artist_id.name=request.form.get('name')
    search_artist_id.city=request.form.get('city')
    search_artist_id.state=request.form.get('state')
    search_artist_id.phone=request.form.get('phone')
    search_artist_id.image_link=request.form.get('image_link')
    search_artist_id.facebook_link=request.form.get('facebook_link')
    search_artist_id.genres=request.form.getlist('genres')
    search_artist_id.website_link=request.form.get('website_link')
    search_artist_id.seeking_venue=bool(request.form.get('seeking_venue'))
    search_artist_id.seeking_description=request.form.get('seeking_description')
    db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter_by(id=venue_id).first()

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  search_venue_id = Venue.query.filter_by(id=venue_id).first()
  if search_venue_id is not None:
    search_venue_id.name = request.form.get('name')
    search_venue_id.city = request.form.get('city')
    search_venue_id.state = request.form.get('state')
    search_venue_id.address = request.form.get('address')
    search_venue_id.phone = request.form.get('phone')
    search_venue_id.image_link = request.form.get('image_link')
    search_venue_id.facebook_link = request.form.get('facebook_link')
    search_venue_id.genres = request.form.getlist('genres')
    search_venue_id.website_link = request.form.get('website_link')
    search_venue_id.seeking_talent = bool(request.form.get('seeking_talent'))
    search_venue_id.seeking_description = request.form.get('seeking_description')
    db.session.commit()

  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  new_artist = Artist(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      phone=request.form.get('phone'),
                      image_link=request.form.get('image_link'),
                      facebook_link=request.form.get('facebook_link'),
                      genres=request.form.getlist('genres'),
                      website_link=request.form.get('website_link'),
                      seeking_venue=bool(request.form.get('seeking_venue')),
                      seeking_description=request.form.get('seeking_description'))
  # TODO: modify data to be the data object returned from db insertion
  try:
    db.session.add(new_artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + new_artist.name + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  show_query = db.session.query(Shows, Venue, Artist)\
    .join(Venue, Venue.id == Shows.venue_id)\
    .join(Artist, Artist.id == Shows.artist_id)\
    .all()
  
  data = []
  for show, venue, artist in show_query:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": venue.name,
      "artist_id": show.artist_id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time":show.start_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form_data = request.form.to_dict()
  # Delete csrf_token if have
  form_data.pop('csrf_token', None)
  try:
    new_show = Shows(**form_data)
    db.session.add(new_show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    #To run with data sample, please uncomment insert_data_sample().
    # insert_data_sample()
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
