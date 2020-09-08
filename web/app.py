from flask import Flask, render_template
import requests
import itertools
from flask_bootstrap import Bootstrap
import os
from get_recommendations import recommend
from flask import request

app = Flask(__name__)
bootstrap = Bootstrap(app)



@app.route('/')
def index():
  
    return render_template('index.html')


@app.route('/recommendations', methods=['GET'])
def recommendations():
    
    song = make = request.args.get('song')
    results = recommend(song)
    if results == False:
        return "Musica não encontrada, por favor tente outra"
    return render_template('playlist.html',  recommendations=recommend(song))


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
