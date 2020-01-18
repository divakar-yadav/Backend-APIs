import traceback,json,pdb
from datetime import date,timedelta,datetime
import pandas as pd
from flask import jsonify
from backEnd.database.db_connection import set_connection
from answergen import create_single_column_response,create_multi_column_response,get_highlight_response
from frontendAPI import city_region_mapping

todays_date = str(datetime.now().date())

def get_table_df(table_name, db_name,movie_name):

    connection = set_connection(db_name)
    # cursor = connection.cursor()
    try:
        table = pd.read_sql(
            'SELECT avg(Seat_Percent) as occupancy,count(*) as shows,Crawl_Hour,City_Name,Movie_Name,Show_date '
            'FROM {0} where Movie_Name = "{1}" and Crawl_Hour = 18 and Show_Date = "{2}" group by '
            'Crawl_Hour,City_Name,Show_Date,Movie_Name'.format(table_name,movie_name,todays_date), con=connection)
        table = table.fillna('')
        table = table.replace('National-Capital-Region-NCR','NCR')
        return table

    except Exception:
        print(traceback.format_exc())

def get_response_city(movie_name,sortby,filterby,groupby=False):

    #default
    mid_txt = " Cities with highest {} are ".format(sortby)
    resp_count = 4
    sort = False
    filterAlais = "Top cities"


    #test alias
    sortbyAlias=sortby
    if sortby.lower() == "occupancy":
        sortbyAlias = "% occupancy"
    if sortby.lower() == "shows":
        sortbyAlias = " shows"

    #filterby drill
    if filterby:

        if "highest" in filterby.lower():
            resp_count = 1
            mid_txt = "City with highest {} is ".format(sortby)
            sort = False
            filterAlais=" Cities with higher {}".format(sortby)

        if "lowest" in filterby.lower():
            resp_count = 1
            mid_txt = "City with lowest {} is ".format(sortby)
            sort = True
            filterAlais = " Cities with lower {}".format(sortby)

    df_table = get_table_df('BMS_Regional_Occupancy', 'disney', movie_name)
    print(df_table)
    df_table['occupancy'] = round(df_table['occupancy'],2)

    cityAns = create_single_column_response(df_table, 'City_Name',mid_txt, n_answer=resp_count, sort_by=sortby,
                                            sort_asc=sort)
    cityAns+='<br><br/>'
    cityAns+=create_multi_column_response(df_table, 'City_Name', sortby, '{} include '.format(filterAlais),
                answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)

    sort = not sort
    cityAns+='<br><br/>'
    cityAns+=create_multi_column_response(df_table, 'City_Name', sortby, " Cities with lower {} include ".format(sortby),
                answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)

    return cityAns

def get_response_performance_city(movie_name,sortby,filterby,groupby=False):

    #default
    mid_txt = " Cities with highest performance {} are ".format(sortby)
    resp_count = 4
    sort = False
    filterAlais = " Cities with high performance"

    #test alias
    # sortbyAlias=sortby
    sortbyAlias = "%"

    #filterby drill
    if filterby:

        if "highest" in filterby.lower():
            resp_count = 1
            mid_txt = "City with highest performance {} is ".format(sortby)
            sort = False
            filterAlais=" Cities with high performance {}".format(sortby)

        if "lowest" in filterby.lower():
            resp_count = 1
            mid_txt = "City with lowest performance {} is ".format(sortby)
            sort = True
            filterAlais = " Cities with low performance {}".format(sortby)

    #get table from Db
    df_table = get_table_df('BMS_Regional_Occupancy', 'disney', movie_name)

    #adding volume, percentage column to df
    df_table = df_with_performance_volume_percentage(df_table)

    print(df_table)
    print(df_table['percentage'].sum())

    #Converting dataframe to readable text response.
    perfAns = create_single_column_response(df_table, 'City_Name',mid_txt, n_answer=resp_count, sort_by=sortby,
                                            sort_asc=sort)
    perfAns+='<br><br/>'
    perfAns+=create_multi_column_response(df_table, 'City_Name', sortby, '{} include '.format(filterAlais),
                answer_suffix=sortbyAlias, answer_prefix=' with approx ',  n_answer=3, sort_by=sortby,
                                          sort_asc=sort)
    print(perfAns)

    sort = not sort
    perfAns+='<br><br/>'
    perfAns+=create_multi_column_response(df_table, 'City_Name', sortby, " Cities with lower performance include ",
                answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)
    return perfAns


def get_response_performance_region(movie_name,sortby,filterby,regionName):

    #default
    mid_txt = " Cities with highest performance {0} in {1} India are ".format(sortby,regionName)
    resp_count = 4
    sort = False
    filterAlais = " Cities with high performance in {} India".format(regionName)

    #test alias
    # sortbyAlias=sortby
    sortbyAlias = "%"

    try:

        #filterby drill
        if filterby:

            if "highest" in filterby.lower():
                resp_count = 1
                mid_txt = "City with highest performance {0} in {1} India is ".format(sortby,regionName)
                sort = False
                filterAlais=" Cities with high performance {0} in {1} India ".format(sortby,regionName)

            if "lowest" in filterby.lower():
                resp_count = 1
                mid_txt = "City with lowest performance {0} in {1} India is ".format(sortby,regionName)
                sort = True
                filterAlais=" Cities with low performance {0} in {1} India ".format(sortby,regionName)

        #get table from Db
        df_table = get_table_df('BMS_Regional_Occupancy', 'disney', movie_name)

        #filtering cities as per region
        city_list = city_region_mapping.region_list[regionName.lower()]
        df_table = df_table[df_table['City_Name'].isin(city_list)]

        #adding volume, percentage column to df
        df_table = df_with_performance_volume_percentage(df_table)

        print(df_table)
        print(df_table['percentage'].sum())

        #Converting dataframe to readable text response.
        perfAns = create_single_column_response(df_table, 'City_Name',mid_txt, n_answer=resp_count, sort_by=sortby,
                                                sort_asc=sort)
        perfAns+='<br><br/>'
        perfAns+=create_multi_column_response(df_table, 'City_Name', sortby, '{} include '.format(filterAlais),
                    answer_suffix=sortbyAlias, answer_prefix=' with approx ',  n_answer=3, sort_by=sortby,
                                              sort_asc=sort)
        print(perfAns)
        sort = not sort
        perfAns+='<br><br/>'
        perfAns+=create_multi_column_response(df_table, 'City_Name', sortby, " Cities with lower performance include ",
                    answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)

    except Exception as e:
        print(e)
        perfAns = "Data for {} is not available".format(regionName)

    return (perfAns)

def get_BMS_likes(movie_name):

    current_date = date_shifter("2019-10-10",0)
    week_before = "2019-10-10"
    yesterday_date = "2019-10-09"
    connection = set_connection('disney')
    table_name = "BMS_User_Likes"
    table = pd.read_sql(
        'SELECT Likes,Crawl_Date from {0} where Movie = "{1}" '
            .format(table_name,movie_name), con=connection)
    table = table.sort_values(by='Crawl_Date')
    print(table)
    ans_likes = ""
    #pdb.set_trace()
    try:
        current_likes = table[table['Crawl_Date']==datetime.now().date()]
        current_likes = int(current_likes['Likes'].values[0])
        print(current_likes)
        ans_likes = "{0} has {1} likes.".format(movie_name,get_highlight_response(current_likes))
        yesterdays_likes = table[table['Crawl_Date']==date_shifter(todays_date,-1)]
        yesterdays_likes = int(yesterdays_likes['Likes'].values[0])
        if yesterdays_likes:
            ans_likes += "<br><br>"
            ans_likes += "Likes has increased by {} since yesterday.".format(get_highlight_response(current_likes-yesterdays_likes))
        likes_week_before = table[table['Crawl_Date']==date_shifter(todays_date,-7)]
        likes_week_before = int(likes_week_before['Likes'].values[0])
        if likes_week_before:
            percentage_increase = (current_likes - likes_week_before)/current_likes*100
            ans_likes += " There is a {}% increase in likes since last week.".format(get_highlight_response(round(percentage_increase,2)))
        print(ans_likes)
    except Exception as e :
        print(e)
        if ans_likes:
            return ans_likes
        else:
            return "Data not available for "+movie_name
    return ans_likes

def get_YT_data(movie_name):

    connection = set_connection('disney')
    table_name = ""
    table = pd.read_sql(
        'SELECT Likes,Views from {0} where Crawl_Date = "2019-10-10" and Movie = "{1}" '.format(table_name,movie_name), con=connection)

def get_distribution_data(movie_name):

    if movie_name == "WAR":
        distribution_table = pd.read_csv('War_2019-10-11.csv')
    elif movie_name == "The Sky is Pink":
        distribution_table = pd.read_csv('The_Sky_Is_Pink_2019-10-11.csv')
    elif movie_name == "Joker":
        distribution_table = pd.read_csv('Joker_2019-10-11.csv')
    else:
        return 'Movie not found'

    atp_national = round(distribution_table['Ticket Price'].mean(axis=0))
    distribution_table = distribution_table.groupby(['Theatre Region']).agg({'Ticket Price': ['mean']})
    print(distribution_table)
    print(atp_national)


    #default
    sortby = "Ticket Price_mean"

    sort = False

    #test alias
    sortbyAlias = "₹"

    distribution_table = flatten_columns(distribution_table)

    distribution_table = distribution_table.reset_index(level=0)
    print(distribution_table)

    perfAns = "Average Ticket Price for {0} is {1}₹.".format(get_highlight_response(movie_name),get_highlight_response(atp_national))

    perfAns+='<br><br>'
    distribution_table = distribution_table.round(2)
    perfAns+=create_multi_column_response(distribution_table, 'Theatre Region', sortby, " Cities with higher Average Ticket Price (ATP) include ",
                answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)
    sort = not sort
    perfAns+='<br><br>'
    perfAns+=create_multi_column_response(distribution_table, 'Theatre Region', sortby, " Cities with lower ATP include are ",
                answer_suffix=sortbyAlias, answer_prefix=' with ',  n_answer=3, sort_by=sortby, sort_asc=sort)

    return perfAns




def date_shifter(date_in,day_shift,string_resp=False):

    date_in = datetime.strptime(date_in,'%Y-%m-%d').date()
    date_out = date_in + timedelta(days=day_shift)
    if not string_resp:
        return date_out
    return str(date_out)


def df_with_performance_volume_percentage(df_in):
    """this function will add volume and volume percentage to the dataframe"""
    #round occupancy
    df_in['occupancy'] = df_in['occupancy'].round()
    #volumne = occupancy*shows
    df_in['Volume'] = df_in['shows']*df_in['occupancy']
    #calculating percentage occupancy
    volSum = df_in['Volume'].sum()
    df_in['percentage'] = round((df_in['Volume'] / volSum)*100,2)

    return df_in

def flatten_columns(df):

    df.columns =  ['_'.join(tup).rstrip('_') for tup in df.columns.values]

    return df
#get_BMS_likes('Frozen 2')
# get_response('Bharat','','shows','')
# get_response_performance_city('Bharat','percentage','highest')
# get_response_performance_region('Bharat','percentage','','All')
# print(get_highlight_response("cacha"))
# print(date_shifter('2019-10-10' ,-1))
# get_distribution_data('Joker')
