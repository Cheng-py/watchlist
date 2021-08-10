from flask import Flask
from flask import url_for

app = Flask(__name__)

@app.route("/")
def hello():
    return "hello"

@app.route("/user/<name>")
def user(name):
    return "Hello %s" %name

@app.route("/test")
def test_url_for():
    print(url_for("hello"))
    print(url_for("user",name='HaHaHa'))
    print(url_for("user",name="LaLaLa"))
    print(url_for("test_url_for"))
    print(url_for("test_url_for",num = 2))
    return "Test Page"