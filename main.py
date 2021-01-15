from flask import Flask, render_template, redirect
from flask_cors import CORS
import os

from gnewsclient import gnewsclient 



# for item in news_list: 
# 	print("Title : ", item['title']) 
# 	print("Link : ", item['link']) 
# 	print("") 


app = Flask(__name__)
# CORS(app)

@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/news/<top>')
def news(top="world"):
	client = gnewsclient.NewsClient(language='english', 
									location='india', 
									topic=f'{top}', 
									max_results=50) 

	news_list = client.get_news() 
	topics = client.topics
	return render_template('news.html', data=news_list, data2=topics)

@app.route('/Text-To-Speech')
def textToSpeech():
	return render_template('TextToSpeech.html')

if __name__ == '__main__':
	app.run(debug=True, port=5000)