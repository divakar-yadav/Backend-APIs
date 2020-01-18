from flask import Flask, escape, request ,jsonify
from sqlalchemy import Column, Date, DateTime, UniqueConstraint,FLOAT, Time,ARRAY, Integer, SMALLINT, VARCHAR, Enum, TIMESTAMP, BOOLEAN
from flask_sqlalchemy import SQLAlchemy
from main import app
from models import Cinemalevel, PrelaunchJsonSerializer
import datetime
from sqlalchemy import func
from sqlalchemy.sql import label
import math,pdb
import traceback
from frontendAPI import executor
from cachier import cachier
import pandas as pd

db = SQLAlchemy(app)


@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/city', methods=['GET'])
def city():

    filterby = request.args.get('filterby')
    movie = request.args.get('movie_name')
    if not movie:
        return ("Please provide movie_name")

    sortby = request.args.get('sortby')
    if not sortby:
        return ("Please provide sortby(shows/occupancy)")

    response = executor.get_response_city(movie,sortby.lower(),filterby)

    return response

@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/city/performance', methods=['GET'])
def city_performance():

    movie = request.args.get('movie_name')
    if not movie:
        return "Please provide movie_name"

    filterby = request.args.get('filterby')
    response = executor.get_response_performance_city(movie,'percentage',filterby)

    return response

@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/region/performance', methods=['GET'])
def region_performance():

    filterby = request.args.get('filterby')

    movie = request.args.get('movie_name')
    if not movie:
        return ("Please provide movie_name")

    regionName = request.args.get('region_name')
    if not regionName:
        return ("Please provide region_name")

    try:
        response = executor.get_response_performance_region(movie,'percentage',filterby,regionName)
    except Exception as e:
        print(e)
        return ("Please provide params - Movie Name and Filterby(Highest / Lowest)")

    return response

@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/bms_likes', methods=['GET'])
def bms_likes():

    movie = request.args.get('movie_name')
    if not movie:
        return ("Please provide movie_name")

    bms_response = executor.get_BMS_likes(movie)

    return bms_response

@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/ATP', methods=['GET'])
def distribution():

    movie = request.args.get('movie_name')
    if not movie:
        return ("Please provide movie_name")

    bms_response = executor.get_distribution_data(movie)

    return bms_response

@cachier(stale_after=datetime.timedelta(days=1))
@app.route('/mobile-screen/questions', methods=['GET'])
def question_list():

    from question_list import questions
    return jsonify(questions)

@cachier(stale_after=datetime.timedelta(hours=1))
@app.route('/mobile-screen/movie_detailed_info', methods=['GET'])
def movie_detailed_info():
    movie = request.args.get('movie_name')
    if not movie:
        return jsonify({"msg": "Please provide movie_name"})

    movies_detailed_info = []
    today_date = datetime.datetime.now().date()
    no = get_records_count()

    try:
        query = db.session.query(
                    func.max(Cinemalevel.movie_name).label("movie"),
                    func.max(Cinemalevel.crawl_hour).label("crawl_hour"),
                    func.max(Cinemalevel.crawl_date).label("crawl_date"),
                    func.avg(Cinemalevel.percent_occupancy).label('percent_occupancy'),
                    func.sum(Cinemalevel.category_occupied_seats).label('tickets_sold'),
                    func.abs(func.sum((Cinemalevel.category_occupied_seats)*(Cinemalevel.category_price))/func.sum(Cinemalevel.category_occupied_seats)).label("avg_price"),
                    func.count(func.distinct(Cinemalevel.show_datetime)).label("shows"))\
                .filter_by(movie_name=movie, show_date=today_date)\
                .group_by(Cinemalevel.movie_name, Cinemalevel.crawl_date, Cinemalevel.crawl_hour)\
                .order_by(Cinemalevel.crawl_date.desc(), Cinemalevel.crawl_hour.desc())\
                .limit(no).all()
        movies_detailed_info = [each._asdict() for each in query]
        # remove the latest crawl as it may be still running, provide one hour ago data
        movies_detailed_info = movies_detailed_info[1:]

    except Exception as err_msg:
        print (err_msg)

    return jsonify({'data': movies_detailed_info, "movie_name": movie})


@cachier(stale_after=datetime.timedelta(hours=1))
@app.route('/mobile-screen/movie_city_detail', methods=['GET'])
def movie_city_detail():
    movie = request.args.get('movie_name')
    city = request.args.get('city_name')
    if not movie:
        return jsonify({"msg": "Please provide movie_name"})
    if not city:
        return jsonify({"msg": "Please provide city_name"})
    movies_detailed_info = []
    today_date = datetime.datetime.now().date()
    no = get_records_count()

    try:
        query = db.session.query(
                    func.max(Cinemalevel.movie_name).label("movie"),
                    func.max(Cinemalevel.crawl_hour).label("crawl_hour"),
                    func.max(Cinemalevel.crawl_date).label("crawl_date"),
                    func.avg(Cinemalevel.percent_occupancy).label('percent_occupancy'),
                    func.sum(Cinemalevel.category_occupied_seats).label('tickets_sold'),
                    func.abs(func.sum((Cinemalevel.category_occupied_seats)*(Cinemalevel.category_price))/func.sum(Cinemalevel.category_occupied_seats)).label("avg_price"),
                    func.count(func.distinct(Cinemalevel.show_datetime)).label("shows")
                )\
                .filter_by(movie_name=movie, city_name=city, show_date=today_date)\
                .group_by(Cinemalevel.movie_name, Cinemalevel.crawl_date, Cinemalevel.crawl_hour)\
                .order_by(Cinemalevel.crawl_date.desc(), Cinemalevel.crawl_hour.desc())\
                .limit(no).all()
        movies_detailed_info = [each._asdict() for each in query]
        movies_detailed_info = movies_detailed_info[1:]

    except Exception as err_msg:
        print (err_msg)

    return jsonify({'data': movies_detailed_info, "movie_name": movie, "city_name": city})



@cachier(stale_after=datetime.timedelta(hours=1))
@app.route('/cinemalevel')
def index():
    movie = request.args.get("movie")
    if not movie:
        return jsonify({"msg": "Please provide movie_name"})

    city = request.args.get("city")
    if not city:
        return jsonify({"msg": "Please provide city"})

    items_per_page = 10
    now = datetime.datetime.now()
    show_date = now.date()
    try:
        query = db.session.query(
            func.array_agg(func.distinct(Cinemalevel.category_occupied_seats)).label('occupancy_trend'),
            func.max(Cinemalevel.movie_name).label("movie"),
            func.max(Cinemalevel.city_name).label("city"),
            func.max(Cinemalevel.venue_name).label('venue_name'),
            func.avg(Cinemalevel.percent_occupancy).label('percent_occupancy'),
            func.abs(func.sum((Cinemalevel.category_occupied_seats)*(Cinemalevel.category_price))/(func.sum(Cinemalevel.category_occupied_seats)+1)).label("avg_price"),
            func.count(func.distinct(Cinemalevel.show_datetime)).label("shows")
        )\
            .filter_by(movie_name=movie, city_name=city, show_date=show_date, crawl_date=show_date)\
            .group_by(Cinemalevel.venue_code)\
            .order_by(func.sum((Cinemalevel.category_occupied_seats)*(Cinemalevel.category_price)).desc())\
            .limit(20).all()
        res_list = [each._asdict() for each in query]

        # no need of pagination till now
        # if request.args.get("page"):
        #     page = int(request.args.get("page"))
        #     if len(res_list) !=0:
        #         if len(res_list) <= items_per_page:
        #             no_of_pages = 1
        #             res = {"data":res_list}
        #             return jsonify(res)
        #         else:
        #             if (len(res_list) % items_per_page) == 0:
        #                 no_of_pages = len(res_list)/items_per_page
        #                 if page < no_of_pages:
        #                     res_list = res_list[page*items_per_page-(items_per_page):page*items_per_page]
        #                     res = {"data":res_list}
        #                     return jsonify(res)
        #                 else:
        #                     res = {"data":[]}
        #                     return jsonify(res)
        #             else:
        #                 no_of_pages = math.floor(len(res_list)/items_per_page) + 1
        #                 if page == no_of_pages:
        #                     last_page_items = len(res_list) % items_per_page
        #                     res_list = res_list[(page)*items_per_page-(items_per_page):((page)*items_per_page+last_page_items)]
        #                     res = {"data":res_list}
        #                     return jsonify(res)
        #                 if page < no_of_pages:
        #                     res_list = res_list[page*items_per_page-(items_per_page):page*items_per_page]
        #                     res = {"data":res_list}
        #                     return jsonify(res)
        #                 if page > no_of_pages:
        #                     res = {"data":[]}
        #                     return jsonify(res)
        #     else:
        #         res = {"data":[]}
        #         return jsonify(res)
        res = {"data":res_list}
        return jsonify(res)
    except Exception as e:
        res = {"message":"Either You are entering parameters in the wrong manner or No shows available Please check the Traceback for more detail"}
        print(traceback.format_exc())
    return jsonify(res)

@app.route('/prelaunch', methods=['GET'])
def prelaunch_screen():
    query =db.session.query(PrelaunchJsonSerializer).all()
    resp = []
    for item in query:
        resp.append({
        'movie_name':item.movie_name,
        'prediction_date':item.prediction_date,
        'release_date':item.release_date,
        'production_house':item.production_house,
        'daily_searches':item.daily_searches,
        'bms_likes_momentum':item.bms_likes_momentum,
        'lower_prediction':item.lower_prediction,
        'upper_prediction':item.upper_prediction,
        'mle':item.mle,
        'comments':item.comments})
    df = pd.DataFrame(resp)
    df = df.sort_values(['prediction_date'],ascending=False)
    df = df.groupby('movie_name').first()
    df = df.dropna()
    df['prediction_date'] = pd.to_datetime(df['prediction_date'])
    df['release_date'] = pd.to_datetime(df['release_date'])
    df_dict = df[df['prediction_date']<df['release_date']]
    df_dict.reset_index(inplace=True)
    return jsonify(df_dict.to_dict(orient = "records"))




def get_records_count():
    now = datetime.datetime.now()
    current_hour = now.hour

    # at an interval of every hour
    todays_crawl = current_hour+1
    
    # at an interval of every 3 hour
    yesterday_crawl = 8 - (current_hour//3)

    return todays_crawl + yesterday_crawl
