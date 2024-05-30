from django.shortcuts import render
from django.db import connection
from .models import Movie
from .models import Actorsinmovies


def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Create your views here.
def home_page(request):
    return render(request, 'home_page.html')



def q1(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT movietitle, genre, rating, gross, releasedate
        FROM Movie;
        """)
        sql_res1 = dictfetchall(cursor)
        genres = []
        for x in sql_res1:
            if genres.count(x['genre']) == 0 and x['genre'] != None:
                genres.append(x["genre"])
        genres.sort()
        results = []
        for genre in genres:
            max_gross = [0, 'empty']
            num_years = []
            max_len = [0, 'empty']
            for x in sql_res1:
                if genre == x['genre']:
                    if int(x['gross']) > max_gross[0]:
                        max_gross[0] = int(x['gross'])
                        max_gross[1] = x['movietitle']
                    if int(len(x['movietitle']) >= max_len[0]):
                        if int(len(x['movietitle']) > max_len[0]):
                            max_len[0] = len(x['movietitle'])
                            max_len[1] = x['movietitle']
                        if int(len(x['movietitle']) == max_len[0]):
                            if max_len[1] > x['movietitle']:
                                max_len[1] = x['movietitle']
                    if num_years.count(x['releasedate'].year) == 0:
                        num_years.append(x['releasedate'].year)
            thisdict = {
                "genre": genre,
                "topGross": max_gross[1],
                "longestName": max_len[1],
                "num_years": len(num_years), }
            results.append(thisdict)
        return results


def q2(request, num):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT movie, actor, actorRole
        FROM Actorsinmovies;
        """)
        sql_res2 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT movietitle, releasedate
        FROM Movie;
        """)
        sql_res3 = dictfetchall(cursor)
        actors = []
        actorsmore = []
        results = []
        for x in sql_res2:
            if actors.count(x['actor']) == 0:
                actors.append(x['actor'])
        for actor in actors:
            count = 0
            for x in sql_res2:
                if x['actor'] == actor:
                    count += 1
            if count >= int(num):
                actorsmore.append(actor)

        for actor in actorsmore:
            oldest = [None, None]
            for v in sql_res2:
                if v['actor'] == actor:
                    for x in sql_res3:
                        if x['movietitle'] == v['movie']:
                            if oldest[0] == None:
                                oldest[0] = x['releasedate']
                                oldest[1] = x['movietitle']
                            elif oldest[0] > x['releasedate']:
                                oldest[0] = x['releasedate']
                                oldest[1] = x['movietitle']
            new_dict = {
                "actor": actor,
                "oldestMovie": oldest[1],
            }
            results.append(new_dict)
        return results


def q3(request):
    with connection.cursor() as cursor:
        cursor.execute("""
       SELECT  actor, rating, count(rating) as count
        FROM(
          SELECT DISTINCT actor, movie, rating
            FROM Movie INNER JOIN Actorsinmovies AIM
                on Movie.movietitle = AIM.movie) as t
                GROUP BY actor, rating 
        """)
        sql_res = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT DISTINCT movie, actor
        FROM Actorsinmovies;
        """)
        sql_res2 = dictfetchall(cursor)
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT movietitle
        FROM Movie;
        """)
        sql_res3 = dictfetchall(cursor)
        actors = []
        only_child_actor = []
        for x in sql_res:
            if actors.count(x['actor']) == 0:
                actors.append(x['actor'])
        for actor in actors:
            G_bool = False
            R_bool = True
            for x in sql_res:
                if actor == x['actor']:
                    if x['rating'] == 'G' and int(x['count']) > 3:
                        G_bool = True
                    if x['rating'] == 'R' and int(x['count']) > 0:
                        R_bool = False
            if G_bool and R_bool:
                only_child_actor.append(actor)
        movies = []
        movies_child = []
        for x in sql_res3:
            if movies.count(x['movietitle']) == 0:
                movies.append(x['movietitle'])
        for movie in movies:
            count_only_child = 0
            for x in sql_res2:
                if movie == x['movie']:
                    if only_child_actor.count(x['actor']) > 0:
                        count_only_child += 1
            movies_child.append([movie, count_only_child])
        top_5 = []
        for i in range(0, 5):
            max = 0
            ind = 0
            for j, x in enumerate(movies_child):
                if x[1] > max:
                    max = x[1]
                    ind = j
            if ind < len(movies_child):
                top_5.append({
                    'Movie': movies_child[ind][0],
                    'Number_of_actors': movies_child[ind][1],
                    })
                del movies_child[ind]
        return top_5


def index(request):
    num = 10000000
    if request.method == 'POST' and request.POST:
        num = request.POST["than"]
    sql_res1 = q1(request)
    sql_res2 = q2(request, num)
    sql_res3 = q3(request)
    return render(request, 'index.html', {'sql_res1': sql_res1, 'sql_res2': sql_res2, 'sql_res3': sql_res3})


def add_movie(request):
    if request.method == 'POST' and request.POST:
        movietitle = request.POST["movietitle"]
        date = request.POST["date"]
        genre = request.POST.get("genre", False)
        rating = request.POST.get("rating", False)
        gross = request.POST["gross"]
        print(movietitle, genre, rating, date, gross)
        new_movie = Movie(movietitle=movietitle,
                          releasedate=date,
                          genre=genre,
                          rating=rating,
                          gross=gross,
                          )
        new_movie.save()
    return render(request, 'add_movie.html')