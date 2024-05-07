
import flask
import csv
from flask import Flask, render_template, request
import difflib
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
from markupsafe import escape

app = flask.Flask(__name__, template_folder='templates')

df2 = pd.read_csv('./model/tmdb.csv')
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(df2['soup'])

cosine_sim2 = cosine_similarity(count_matrix, count_matrix)

df2 = df2.reset_index()
indices = pd.Series(df2.index, index=df2['title'])
all_titles1 = [df2['title'][i] for i in range(len(df2['title']))]
def get_recommendations(title):
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:25]
    movie_indices = [i[0] for i in sim_scores]
    tit = df2['title'].iloc[movie_indices]
    dat = df2['release_date'].iloc[movie_indices]
    rating = df2['vote_average'].iloc[movie_indices]
    moviedetails=df2['overview'].iloc[movie_indices]
    movietypes=df2['keywords'].iloc[movie_indices]
    movieid=df2['id'].iloc[movie_indices]

    return_df = pd.DataFrame(columns=['Title','Year'])
    return_df['Title'] = tit
    return_df['Year'] = dat
    return_df['Ratings'] = rating
    return_df['Overview']=moviedetails
    return_df['Types']=movietypes
    return_df['ID']=movieid
    return return_df

def get_suggestions():
    data = pd.read_csv('tmdb.csv')
    return list(data['title'].str.capitalize())

app = Flask(__name__)

@app.route("/")
@app.route("/index")
def index():
    NewMovies=[]
    global names1,dates1,ratings1,overview1,types1,mid1, m_name1,result_final1
    with open('movieR.csv','r') as csvfile:
        readCSV = csv.reader(csvfile)
        NewMovies.append(random.choice(list(readCSV)))
    m_name1 = NewMovies[0][0]
    m_name1 = m_name1.title()

    with open('movieR.csv', 'a',newline='') as csv_file:
        fieldnames = ['Movie']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow({'Movie': m_name1})
        result_final = get_recommendations(m_name1)
        names1 = []
        dates1 = []
        ratings1 = []
        overview1=[]
        types1=[]
        mid1=[]
        for i in range(len(result_final)):
            names1.append(result_final.iloc[i][0])
            dates1.append(result_final.iloc[i][1])
            ratings1.append(result_final.iloc[i][2])
            overview1.append(result_final.iloc[i][3])
            types1.append(result_final.iloc[i][4])
            mid1.append(result_final.iloc[i][5])
    suggestions = get_suggestions()

    return render_template('index.html',suggestions=suggestions,movie_type=types1[25:],movieid=mid1,movie_overview=overview1,movie_names=names1,movie_date=dates1,movie_ratings=ratings1,search_name=m_name1)

# Set up the main route
@app.route('/positive', methods=['GET', 'POST'])
def main():
    if flask.request.method == 'GET':
        return(flask.render_template('index.html'))

    if flask.request.method == 'POST':
        m_name = flask.request.form['movie_name']
        m_name = m_name.title()

        if m_name not in all_titles1:
            suggestions=get_suggestions()
            not_found=True
            return render_template('index.html',suggestions=suggestions,not_found=not_found,movie_type=types1[25:],movieid=mid1,movie_overview=overview1,movie_names=names1,movie_date=dates1,movie_ratings=ratings1,search_name=m_name)
        else:
            not_found=False
            with open('movieR.csv', 'a',newline='') as csv_file:
                fieldnames = ['Movie']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow({'Movie': m_name})
            result_final = get_recommendations(m_name)
            names = []
            dates = []
            ratings = []
            overview=[]
            types=[]
            mid=[]
            for i in range(len(result_final)):
                names.append(result_final.iloc[i][0])
                dates.append(result_final.iloc[i][1])
                ratings.append(result_final.iloc[i][2])
                overview.append(result_final.iloc[i][3])
                types.append(result_final.iloc[i][4])
                mid.append(result_final.iloc[i][5])

            return flask.render_template('positive.html',movie_type=types[25:],movieid=mid,movie_overview=overview,movie_names=names,movie_date=dates,movie_ratings=ratings,search_name=m_name)

if __name__ == '__main__':
    app.run()
