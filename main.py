from flask import Flask, render_template, redirect, request, flash, url_for, session
from flask_cors import CORS
import os
import os.path
from werkzeug.security import generate_password_hash, check_password_hash

from gnewsclient import gnewsclient
import sqlite3

import requests
from bs4 import BeautifulSoup

# result = requests.get('http://brainden.com/logic-riddles.htm')
# result = requests.get('https://www.getriddles.com/hard-riddles/')
# page = result.text

# soup = BeautifulSoup(page, 'html.parser')

# riddles = soup.find_all('div', {'class':'et_pb_text_inner'})

# print(riddles)


def returnStuff(link):  # return image and description
    result = requests.get(f"{link}")
    page = result.text
    soup = BeautifulSoup(page, "html.parser")
    getMetaImage = soup.find_all("meta", {"property": "og:image"}, content=True)
    getMetaDesc = soup.find_all("meta", {"property": "og:description"}, content=True)
    linkList = []
    descList = []
    for a in getMetaImage:
        linkList.append(a["content"])
    for d in getMetaDesc:
        descList.append(d["content"])
    return (linkList, descList)


app = Flask(__name__)
app.config["SECRET_KEY"] = "mysecretkey_is_safe"

BASE_DIR = os.getcwd()
db_path = f"{BASE_DIR}/static/user.db"


@app.route("/")
@app.route("/home")
def home():
    if "user" in session:
        # print(session["user"])
        return render_template("home.html", username=session["user"])
    else:
        return redirect(url_for("login"))


@app.route("/news/<top>")
def news(top="world"):

    client = gnewsclient.NewsClient(
        language="english",
        location="United States",
        topic=f"{top}",
        max_results=5,
    )
    news_list = client.get_news()
    # returnImage(news_list.link[0])
    for item in news_list:
        print((returnStuff(item["link"])))

    topics = client.topics
    if "user" in session:
        # print(session["user"])
        return render_template(
            "dataNews.html",
            username=session["user"],
            data=news_list,
            data2=topics,
            len=5,
        )
    else:
        return redirect(url_for("login"))
    # return render_template("news.html", data=news_list, data2=topics)


@app.route("/Text-To-Speech")
def textToSpeech():
    if "user" in session:
        # print(session["user"])
        return render_template("TextToSpeech1.html", username=session["user"])
    else:
        return redirect(url_for("login"))

    # return render_template("TextToSpeech1.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        session.pop("user", None)
    if request.method == "POST":

        if request.form["CheckLogReg"] == "register":
            RegisterUserName = request.form["RegisterUserName"]
            RegisterPassword = generate_password_hash(request.form["RegisterPassword"])
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            db.execute(
                f"INSERT INTO login ('username', 'password') values('{RegisterUserName}','{RegisterPassword}')"
            )
            conn.commit()
            conn.close()
            print(RegisterUserName)
            print(RegisterPassword)

        elif request.form["CheckLogReg"] == "login":
            conn = sqlite3.connect(db_path)
            db = conn.cursor()
            LoginUserName = request.form["LoginUserName"]
            LoginPassWord = request.form["LoginPassword"]
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


@app.route("/test")
def test():
    return f"blah blah <br> yes"


if __name__ == "__main__":
    app.run(debug=True, port=5000)
