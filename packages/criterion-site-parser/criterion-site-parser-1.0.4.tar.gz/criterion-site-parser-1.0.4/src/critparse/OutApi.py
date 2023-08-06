import json
from collections import namedtuple


def call_api(movies_list, series_name):
    MovieInfo = namedtuple("MovieInfo", "just_title year title director country stars descr length url")
    episode = 0
    for movie in movies_list:
        episode += 1
        movie_info = MovieInfo(*movie)
        addViaApi(movie_info, series_name)


def addViaApi(movie, collection=None, supplied_length=None):
    put_uri = "http://localhost:8080/rest/movie"
    movie_dto = {"title": movie.just_title,
                 "year": movie.year,
                 "actors": movie.stars,
                 "directors": movie.director,
                 "countries": movie.country,
                 "collections": collection,
                 "description": movie.descr}
    movie_length = movie.length
    if supplied_length:
        movie_length = supplied_length
    movie_dto["duration"] = movie_length

    # print the json instead of calling api
    print(json.dumps(movie_dto))
    # response = requests.put(put_uri, json=movie_dto)
    # if response.status_code != 200:
    #     print("Error")
