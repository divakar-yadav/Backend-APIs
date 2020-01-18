from sqlalchemy import func
from sqlalchemy import Column, Date, DateTime, UniqueConstraint,FLOAT, Time, Integer, SMALLINT, VARCHAR, Enum, TIMESTAMP, BOOLEAN
from flask_sqlalchemy import SQLAlchemy
from main import app
from config import SQLALCHEMY_DATABASE_URI
from helpers import JsonSerializer
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
db = SQLAlchemy(app)

class CinemalevelJsonSerializer(JsonSerializer):
    def to_json(self):
        res = super(CinemalevelJsonSerializer, self).to_json()
        date = res.pop('crawl_date')
        res.update({'crawl_date':date.isoformat()})
        return res
class Cinemalevel(db.Model,CinemalevelJsonSerializer):
    __tablename__ = "movie_occupancy_bms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_name = Column(VARCHAR(length=64), index=True)
    city_name = Column(VARCHAR(length=64), index=True)
    venue_code = Column(VARCHAR(length=16))
    venue_name = Column(VARCHAR(length=64))
    show_date = Column(Date, index=True)
    show_time = Column(VARCHAR(length=16))
    show_datetime = Column(DateTime(timezone=True))
    show_language = Column(VARCHAR(length=32), index=True)
    category_price = Column(SMALLINT)
    category_max_seats = Column(SMALLINT)
    category_occupied_seats = Column(SMALLINT)
    crawl_hour = Column(SMALLINT, index=True)
    crawl_date = Column(Date, index=True)
    percent_occupancy = Column(FLOAT, index=True)

class PrelaunchJsonSerializer(db.Model):
    __tablename__ = "pre_launch_automated"
    id = Column(Integer,primary_key=True,autoincrement = True)
    movie_name = Column(VARCHAR(length=64), index=True)
    prediction_date = Column(DateTime(timezone=True))
    release_date = Column(DateTime(timezone=True))
    production_house = Column(VARCHAR(length=64))
    daily_searches = Column(SMALLINT)
    bms_likes_momentum = Column(SMALLINT)
    lower_prediction = Column(SMALLINT)
    upper_prediction = Column(SMALLINT)
    mle = Column(SMALLINT)
    comments = Column(VARCHAR(length=64), index=True)



