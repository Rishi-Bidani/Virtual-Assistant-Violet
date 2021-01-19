from flask import Flask, render_template, redirect, request, flash, url_for, session
from flask_cors import CORS
import os
import os.path
from werkzeug.security import generate_password_hash, check_password_hash

from gnewsclient import gnewsclient
import sqlite3

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey_is_safe"

BASE_DIR = os.getcwd()
db_path = f"{BASE_DIR}/static/user.db"


def returnStuff(link):  # return image and description
    result = requests.get(f"{link}")
    page = result.text
    soup = BeautifulSoup(page, "html.parser")
    getMetaImage = soup.find_all(
        "meta", {"property": "og:image"}, content=True)
    getMetaDesc = soup.find_all(
        "meta", {"property": "og:description"}, content=True)
    linkList = []
    descList = []
    for a in getMetaImage:
        linkList.append(a["content"])
    for d in getMetaDesc:
        descList.append(d["content"])

    return (linkList, descList)


def addToNews(top):
    client = gnewsclient.NewsClient(
        language="english",
        location="United States",
        topic=f"{top}",
        max_results=7,
    )
    news_list = client.get_news()
    for item in news_list:
        conn = sqlite3.connect(db_path)
        db = conn.cursor()
        returnStuffTuple = (returnStuff(item["link"]))
        summ = "No Summary"
        img = "No Image"
        try:
            summ = "" if returnStuffTuple[1][0] == (
            ) else returnStuffTuple[1][0]
            img = "" if returnStuffTuple[0][0] == (
            ) else returnStuffTuple[0][0]

        except IndexError:
            pass

        db.execute(
            "INSERT OR IGNORE INTO news('heading', 'summary', 'link', 'image', 'topic') VALUES(?,?,?,?,?)", (
                item['title'], summ, item['link'], img, top)
        )
        conn.commit()
        conn.close()


topics = ['Top Stories',
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
    addToNews(f'{top}')

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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
