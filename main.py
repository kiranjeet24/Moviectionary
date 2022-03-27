import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import requests
from tmdbv3api import TMDb
from tmdbv3api import Movie
tmdb = TMDb()

data = pd.read_csv('main_data.csv')

def create_similarity():
    # data = pd.read_csv('main_data.csv')
    # creating a count matrix
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(data['comb'].values.astype('U'))
    # creating a similarity score matrix
    similarity = cosine_similarity(count_matrix)
    return data,similarity

def rcmd(m):
    m = m.lower()
    try:
        global data
        data.head()
        similarity.shape
    except:
        #data, similarity = create_similarity()
        if m not in data['movie_title'].unique():
            tmdb_movie = Movie()
            tmdb.api_key = '6c2459e44e0b6c41de8d3c8c0a6e8d80'
            genres = []
            genre_str=''
            result = tmdb_movie.search(m)
            if not result:
                print("Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies.")

            movie_id = result[0].id
            response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
            data_json = response.json()
            if data_json['genres']:
                for i in range(0,len(data_json['genres'])):
                    genres.append(data_json['genres'][i]['name'])
                genre_str = genre_str.join(genres)
            else:
                np.NaN
            
            response1 = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}&language=en-US".format(movie_id,tmdb.api_key))
            actorsname =[]
            data_json = response1.json()
            if data_json['cast']:
                for i in range(0,3):
                    actorsname.append(data_json['cast'][i]['name'])
            else:
                for i in range(0,3):
                    actorsname.append('unknown')
            
            response2 = requests.get("https://api.themoviedb.org/3/movie/{}/credits?api_key={}&language=en-US".format(movie_id,tmdb.api_key))
            directorsname =[]
            data_json = response2.json()
            for i in range(0,len(data_json['crew'])):
                if data_json['crew'][i]["job"]=='Director':
                    directorsname.append(data_json['crew'][i]['name'])
            if len(directorsname)==0:
                directorsname.append('unknown')
            
            #df2 = pd.DataFrame({'movie_title': [m]  ,'actor_1_name': [actorsname[0]], 'actor_2_name': [actorsname[1]], 'actor_3_name': [actorsname[2]],'director_name':[directorsname[0]],'genres':[ genre_str]})
            
            comb = actorsname[0] + ' ' + actorsname[1] + ' '+ actorsname[2] + ' '+ directorsname[0] +' ' + genre_str
            
            data.loc[len(data.index)] = [directorsname[0],actorsname[0],actorsname[1],actorsname[2],genre_str,m,comb]
            
            # data = data.append(df2, ignore_index = True)
            #data = pd.concat([data,df2],ignore_index=True,axis=0)
            data, similarity = create_similarity()
            
            i = data.loc[data['movie_title']==m].index[0]
            lst = list(enumerate(similarity[i]))
            lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
            lst = lst[1:11] # excluding first item since it is the requested movie itself
            l = []
            for i in range(len(lst)):
                a = lst[i][0]
                l.append(data['movie_title'][a])
            data.to_csv('main_data.csv',index=False)
            return l


#return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
        else:
            data, similarity = create_similarity()
            i = data.loc[data['movie_title']==m].index[0]
            lst = list(enumerate(similarity[i]))
            lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
            lst = lst[1:11] # excluding first item since it is the requested movie itself
            l = []
            for i in range(len(lst)):
                a = lst[i][0]
                l.append(data['movie_title'][a])
            return l
    
# converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
def convert_to_list(my_list):
    my_list = my_list.split('","')
    my_list[0] = my_list[0].replace('["','')
    my_list[-1] = my_list[-1].replace('"]','')
    return my_list

def get_suggestions():
    data = pd.read_csv('main_data.csv')
    return list(data['movie_title'].str.capitalize())

app = Flask(__name__)

@app.route("/")
@app.route("/home")
def home():
    suggestions = get_suggestions()
    return render_template('home.html',suggestions=suggestions)

@app.route("/similarity",methods=["POST"])
def similarity():
    movie = request.form['name']
    rc = rcmd(movie)
    if type(rc)==type('string'):
        return rc
    else:
        m_str="---".join(rc)
        return m_str

@app.route("/recommend",methods=["POST"])
def recommend():
    # getting data from AJAX request
    title = request.form['title']
    cast_ids = request.form['cast_ids']
    cast_names = request.form['cast_names']
    cast_chars = request.form['cast_chars']
    cast_bdays = request.form['cast_bdays']
    cast_bios = request.form['cast_bios']
    cast_places = request.form['cast_places']
    cast_profiles = request.form['cast_profiles']
    imdb_id = request.form['imdb_id']
    poster = request.form['poster']
    genres = request.form['genres']
    overview = request.form['overview']
    vote_average = request.form['rating']
    vote_count = request.form['vote_count']
    release_date = request.form['release_date']
    runtime = request.form['runtime']
    status = request.form['status']
    rec_movies = request.form['rec_movies']
    rec_posters = request.form['rec_posters']

    # get movie suggestions for auto complete
    suggestions = get_suggestions()

    # call the convert_to_list function for every string that needs to be converted to list
    rec_movies = convert_to_list(rec_movies)
    rec_posters = convert_to_list(rec_posters)
    cast_names = convert_to_list(cast_names)
    cast_chars = convert_to_list(cast_chars)
    cast_profiles = convert_to_list(cast_profiles)
    cast_bdays = convert_to_list(cast_bdays)
    cast_bios = convert_to_list(cast_bios)
    cast_places = convert_to_list(cast_places)
    
    # convert string to list (eg. "[1,2,3]" to [1,2,3])
    cast_ids = cast_ids.split(',')
    cast_ids[0] = cast_ids[0].replace("[","")
    cast_ids[-1] = cast_ids[-1].replace("]","")
    
    # rendering the string to python string
    for i in range(len(cast_bios)):
        cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"','\"')
    
    # combining multiple lists as a dictionary which can be passed to the html file so that it can be processed easily and the order of information will be preserved
    movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
    
    casts = {cast_names[i]:[cast_ids[i], cast_chars[i], cast_profiles[i]] for i in range(len(cast_profiles))}

    cast_details = {cast_names[i]:[cast_ids[i], cast_profiles[i], cast_bdays[i], cast_places[i], cast_bios[i]] for i in range(len(cast_places))}

    # passing all the data to the html file
    return render_template('recommend.html',title=title,poster=poster,overview=overview,vote_average=vote_average,
        vote_count=vote_count,release_date=release_date,runtime=runtime,status=status,genres=genres,
        movie_cards=movie_cards,casts=casts,cast_details=cast_details)

if __name__ == '__main__':
    app.run(debug=True)
