from flask import Flask, render_template, redirect, request, flash, url_for, session, send_from_directory
from flask_cors import CORS
import os
import os.path
from werkzeug.security import generate_password_hash, check_password_hash

from gnewsclient import gnewsclient
import sqlite3

import requests
from bs4 import BeautifulSoup

from recipe_scraper import RecipeModule, Dish
from getRecipes import getSearchResults, getRecipeDetails
import json

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey_is_safe"

BASE_DIR = os.getcwd()
db_path = f"{BASE_DIR}/static/user.db"


class News:
    def runGClient(self, topic):
        client = gnewsclient.NewsClient(
            language="english",
            location="United States",
            topic=f"{topic}",
            max_results=10,
        )
        return client.get_news()

    def returnImageandSummary(self, link):
        image = ""
        desc = ""
        result = requests.get("https://www.bbc.com/news")
        try:
            result = requests.get(f"{link}", timeout=2)
        except requests.exceptions.Timeout as e:
            # Maybe set up for a retry
            print(e)
        page = result.text

        soup = BeautifulSoup(page, "html.parser")

        # print(soup)

        getMetaImage = soup.find_all(
            "meta", {"property": "og:image"}, content=True)
        getMetaDesc = soup.find_all(
            "meta", {"property": "og:description"}, content=True)

        for i in getMetaImage:
            image = i["content"]
        for d in getMetaDesc:
            desc = d["content"]
        print(image)
        print(desc)
        print()
        return (image, desc)

    def addNewsToDatabase(self, topic):
        news_list = self.runGClient(topic)
        for item in news_list:
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            ImageAndDesc = self.returnImageandSummary(item["link"])
            summ = ImageAndDesc[1]
            img = ImageAndDesc[0]
            db.execute(
                "INSERT OR IGNORE INTO news('heading', 'summary', 'link', 'image', 'topic') VALUES(?,?,?,?,?)", (
                    item['title'], summ, item['link'], img, topic)
            )
            conn.commit()
            conn.close()


scrapeNews = News()

topics = [
    'World',
    'Nation',
    'Business',
    'Technology',
    'Entertainment',
    'Sports',
    'Science',
    'Health']


def getTopNewsBBC():
    result = requests.get("https://www.bbc.com/news/world")
    page = result.text
    soup = BeautifulSoup(page, "html.parser")

    images = soup.find('div', {
        "class": "gs-o-responsive-image gs-o-responsive-image--16by9 gs-o-responsive-image--lead"}).findChildren('img')

    headline = soup.find('h3', {
                         'class': "gs-c-promo-heading__title gel-paragon-bold gs-u-mt+ nw-o-link-split__text"})

    summary = soup.find(
        'p', {'class': 'gs-c-promo-summary gel-long-primer gs-u-mt nw-c-promo-summary'})

    imgs = ""
    heading = ""
    summ = ""

    for head in headline:
        heading = head

    for sumry in summary:
        summ = sumry

    for img in images:
        imgs = img.get('src')

    return [imgs, heading, summ]


@app.route("/")
def homeScreen():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    else:
        return render_template("welcome_page.html")

@app.route("/home")
def home():
    if "user" in session:
        return render_template("home.html", username=session["user"])
    else:
        return redirect(url_for("login"))


@ app.route("/news/<top>")
def news(top="world"):

    topNewsData = getTopNewsBBC()

    conn = sqlite3.connect(db_path)

    db = conn.cursor()
    db.execute(
        f"DELETE FROM news WHERE topic = '{top}'"
    )
    conn.commit()
    conn.close()
    # addToNews(f'{top}')
    scrapeNews.addNewsToDatabase(f'{top}')

    conn = sqlite3.connect(db_path)
    db = conn.cursor()
    summ1 = db.execute(
        f"SELECT heading, summary, image, link FROM news WHERE topic='{top}'")
    summary = summ1.fetchall()

    newdict = {}

    for i in range(len(summary)):
        newdict[f'{summary[i][0]}'] = [
            str(summary[i][1])[0:400] + "...", summary[i][2], summary[i][3]]

    # print(newdict)

    if "user" in session:
        # print(session["user"])
        return render_template(
            "dataNews.html",
            username=session["user"],
            # data=news_list,
            data=newdict,
            data2=topics,
            topNews=topNewsData
        )
    else:
        return redirect(url_for("login"))
    # return render_template("news.html", data=news_list, data2=topics)


@ app.route("/Text-To-Speech")
def textToSpeech():
    if "user" in session:
        # print(session["user"])
        return render_template("TextToSpeech1.html", username=session["user"])
    else:
        return redirect(url_for("login"))

    # return render_template("TextToSpeech1.html")


@ app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        session.pop("user", None)
    if request.method == "POST":

        if request.form["CheckLogReg"] == "register":
            RegisterUserName = request.form["RegisterUserName"]
            RegisterPassword = generate_password_hash(
                request.form["RegisterPassword"])
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            db.execute(
                f"INSERT INTO login ('username', 'password') values('{RegisterUserName}','{RegisterPassword}')"
            )
            conn.commit()
            conn.close()
            # print(RegisterUserName)
            # print(RegisterPassword)

        elif request.form["CheckLogReg"] == "login":
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            LoginUserName = request.form["LoginUserName"]
            # LoginPassWord = request.form["LoginPassword"]
            password = db.execute(
                f"SELECT password from login WHERE username = '{LoginUserName}'"
            )

            hashPass = password.fetchone()[0]

            if check_password_hash(hashPass, request.form["LoginPassword"]):
                session["user"] = LoginUserName
                # return render_template("home.html")
                return redirect(url_for("home"))
            else:
                return render_template("login.html", data="fail")

            conn.close()

        else:
            return render_template("404.html")

    return render_template("login.html")


@app.route('/recipes', methods=["GET", "POST"])
def recipes():
    # dish_names = []
    if "user" in session:
        data = {'titles': [], 'prepTime': [],
                'cookTime': [], 'servings': [], 'links': []}
        if request.method == "POST" and request.form.get("searching") == "search":
            recipename = request.form.get("recipe_search")
            print(recipename)
            # module = RecipeModule(recipename)
            module = getSearchResults(recipename)
            dish_names = module.returnTitles()
            prepTime, cookTime, servings = module.returnTitleDetails()
            links = module.returnLinks()

            data = {'titles': dish_names, 'prepTime': prepTime,
                    'cookTime': cookTime, 'servings': servings, 'links': links}
            # for links in data['links']:

        else:
            print("didnt work")
        return render_template("recipes.html", username=session["user"], data=data)

    else:
        return redirect(url_for("login"))


@app.route("/recipes/<name>")
def displayRecipe(name):
    print("print link: ", name)
    data = {}

    module = getSearchResults(name)
    links = module.returnLinks()[:1]
    module2 = getRecipeDetails(links[0])
    data['title'] = name
    data['link'] = links[0]
    data['procedure'] = module2.returnProcedure()
    data['ingredients'] = module2.returnIngredients()
    data['chef'] = module2.returnChef()
    data['servings'] = module2.returnServings()
    data['preptime'] = module2.returnPrepTime()
    data['cooktime'] = module2.returnCookingTime()
    return render_template("displayrecipes.html", data=data, username=session["user"])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                          'favicon.ico')
if __name__ == "__main__":
    app.run(debug=True, port=5000)
