from flask import Flask,render_template,request,flash,redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,LoginManager,UserMixin,login_required, logout_user,current_user
# app = Flask(__name__)
name = 'Old C'

# @app.route('/')
# def index():
#     return render_template('index.html', name=name, movies=movies)
#
# @app.route("/user/<name>")
# def user(name):
#     return "Hello %s" %name
#
# @app.route("/test")
# def test_url_for():
#     print(url_for("hello"))
#     print(url_for("user",name='HaHaHa'))
#     print(url_for("user",name="LaLaLa"))
#     print(url_for("test_url_for"))
#     print(url_for("test_url_for",num = 2))
#     return "Test Page"


WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"

app = Flask(__name__)

movies = [
{'title': 'My Neighbor Totoro', 'year': '1988'},
{'title': 'Dead Poets Society', 'year': '1989'},
{'title': 'A Perfect World', 'year': '1993'},
{'title': 'Leon', 'year': '1994'},
{'title': 'Mahjong', 'year': '1996'},
{'title': 'Swallowtail Butterfly', 'year': '1996'},
{'title': 'King of Comedy', 'year': '1999'},
{'title': 'Devils on the Doorstep', 'year': '1999'},
{'title': 'WALL-E', 'year': '2008'},
{'title': 'The Pork of Music', 'year': '2012'},
]
app.config['SQLALCHEMY_DATABASE_URI'] =prefix + os.path.join(app.root_path, 'data.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # 关闭对模型修改的监控
app.config["SECRET_KEY"] ="dev"

db = SQLAlchemy(app)  # 在拓展类实例化前加载配置


login_manager = LoginManager(app)






@app.cli.command() # 创建数据库
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20)) # 用户名
    password_hash = db.Column(db.String(128)) # 密码散列值
    def set_password(self, password): # 用来设置密码的方法， 接受密码作为参数
        self.password_hash = generate_password_hash(password) #将生成的密码保持到对应字段

    def validate_password(self, password): # 用于验证密码的方法， 接受密码作为参数
        return check_password_hash(self.password_hash, password)
# 返回布尔值
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    year = db.Column(db.String(4))

@app.cli.command()
def forge():  # 执行 flask forge 命令就会把所有虚拟数据添加到数据库里：
    """Generate fake data."""
    db.create_all()
    # 全局的两个变量移动到这个函数内
    name = 'Old C'
    movies = [
    {'title': 'My Neighbor Totoro', 'year': '1988'},
    {'title': 'Dead Poets Society', 'year': '1989'},
    {'title': 'A Perfect World', 'year': '1993'},
    {'title': 'Leon', 'year': '1994'},
    {'title': 'Mahjong', 'year': '1996'},
    {'title': 'Swallowtail Butterfly', 'year': '1996'},
    {'title': 'King of Comedy', 'year': '1999'},
    {'title': 'Devils on the Doorstep', 'year': '1999'},
    {'title': 'WALL-E', 'year': '2008'},
    {'title': 'The Pork of Music', 'year': '2012'},
    ]
    user = User(name=name)
    db.session.add(user)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.commit()
    click.echo('Done.')



@app.cli.command()
@click.option('--username',prompt = True, help = "the username used to Login.")
@click.option("--password",prompt = True , hide_input = True, confirmation_prompt = True, help = " The Password Used to Login.")
def admin(username, password):
    """create user"""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo("Updating user...")
        user.username = username
        user.set_password(password)
    else:
        click.echo("Creating user...")
        user = User(username = username,name = "Admin")
        user.set_password(password)
        db.session.add(user)
    db.session.commit()
    click.echo("Done.")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': # 判断是否是 POST 请求
        # 获取表单数据
        title = request.form.get('title') # 传入表单对应输入字段的name 值
        year = request.form.get('year')
# 验证数据
        if not title or not year or len(year) > 4 or len(title)> 60:
            flash('Invalid input.') # 显示错误提示
            return redirect(url_for('index')) # 重定向回主页
# 保存表单数据到数据库
        movie = Movie(title=title, year=year) # 创建记录
        db.session.add(movie) # 添加到数据库会话
        db.session.commit() # 提交数据库会话
        flash('Item created.') # 显示成功创建的提示
        return redirect(url_for('index')) # 重定向回主页
    user = User.query.first()
    movies = Movie.query.all()
    return render_template('index.html', user=user, movies=movies)

@app.route('/movie/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        title = request.form['title']
        year = request.form['year']

        if not title or not year or len(year) > 4 or len(title) > 60:
            flash('Invalid input.')
            return redirect(url_for('edit', movie_id=movie_id))
        movie.title = title
        movie.year = year
        db.session.commit()
        flash('Item updated.')
        return redirect(url_for('index'))

    return render_template('edit.html', movie=movie)


@app.route('/movie/delete/<int:movie_id>', methods=['POST'])
def delete(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    flash('Item deleted.')
    return redirect(url_for('index'))


# login_manager.login_view = 'login'
@app.route("/login",methods = ["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            flash("Invalid input")
            return redirect(url_for("login"))
        user = User.query.first()
        #  验证用户名和密码是否一致
        if username == username and user.validate_password(password):
            login_user(user)
            flash("Login Success")
            return redirect(url_for("index"))

        flash("Invalid username or password")
        return redirect(url_for("login"))
    return render_template("login.html")



@app.route("/logout")
@login_required # 保护视图
def logout():
    logout_user() # 登出用户
    flash("GoodBye~~~")
    return redirect(url_for("index"))


@app.context_processor
def inject_user(): # 函数名可以随意修改
    user = User.query.first()
    return dict(user=user) # 需要返回字典， 等同于return {'user': user}


@login_manager.user_loader
def load_user(user_id): # 创建用户加载回调函数， 接受用户 ID 作为参数
    user = User.query.get(int(user_id)) # 用 ID 作为 User 模型的主键查询对应的用户
    return user # 返回用户对象







@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html') ,404




