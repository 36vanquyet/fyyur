from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY

db = SQLAlchemy()

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