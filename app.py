from main import SudokuMaker, SudokuChecker

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import Required, Email, Length, EqualTo


from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask.ext.mail import Mail, Message

from werkzeug.security import generate_password_hash, check_password_hash

from threading import Thread
from copy import deepcopy
from ast import literal_eval
import os


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = "k1dYmvbK6uJWdMybTKk8zdYoNW"

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.session_protection= "strong"
login_manager.login_view = "login"
login_manager.init_app(app)


app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")

app.config['SUDOKU_MAIL_SUBJECT_PREFIX'] = '[sudokugame.herokuapp.com]'
app.config['SUDOKU_MAIL_SENDER'] = "Online Sudoku Admin <" + os.environ.get("MAIL_USERNAME") + ">"
app.config['SUDOKU_ADMIN'] = os.environ.get("MAIL_USERNAME")

mail = Mail(app)


#########################################################################################################

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(512))
    easy = db.Column(db.Integer, default=0)
    normal = db.Column(db.Integer, default=0)
    hard = db.Column(db.Integer, default=0)
    evil = db.Column(db.Integer, default=0)
    total_games = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<tr> <td>" + self.username + "</td> <td>" + str(self.easy) + "</td>" + \
                    "<td>" + str(self.normal) + "</td> <td>" + str(self.hard) + "</td>" + \
                    "<td>" + str(self.evil) + "</td> <td>" + str(self.total_games) + "</td>" + \
                    "<td>" + str(self.points) + "</td> </tr>"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#########################################################################################################

class LoginForm(Form):
    email = StringField("Email:", validators=[Required(), Length(1,64), Email()])
    password = PasswordField("Password:", validators=[Required()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")

#########################################################################################################

class RegistrationForm(Form):
    username = StringField('Username', validators=[Required(), Length(1, 64)])
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

#########################################################################################################

def make_session():
    if "solved" not in session:
        session["solved"] = []

    if "email" not in session:
        session["email"] = ""

#########################################################################################################

def make_game(difficultLevel):
    make_session()

    levelsText = {1: "easy", 2: "normal", 3 : "hard", 4: "evil"}
    difficultText = levelsText[difficultLevel]
    template = "game.html"


    if len(request.form) > 0:
        checkTable = literal_eval(request.form["table"])
        table = literal_eval(request.form["table"])

        for row in range(len(table) + 1):
            for col in range(len(table) + 1):
                name = str(row)+str(col)
                if name in request.form:
                    if request.form[name].isdigit():
                        checkTable[row][col] = int(request.form[name])
                        table[row][col] = -int(request.form[name])
                    else:
                        checkTable[row][col] = 0
                        table[row][col] = 0

        checkSudoku = SudokuChecker(checkTable)

        if not checkSudoku.checkTable():
            alert_type = 1
            flash("Incorrect decision!")
            return render_template(template, table=table, alert_type=alert_type, difficult= difficultText, \
                                   visibleCells = request.form["visibleCells"], hiddenCells=request.form["hiddenCells"])
        else:
            if checkTable not in session["solved"]:
                session["solved"].append(checkTable)
                user = User.query.filter_by(email = session["email"]).first()
                if user is not None:
                    points_dict = {1 : "user.easy += 1", 2 : "user.normal += 1", 3 : "user.hard += 1", 4 : "user.evil += 1"}
                    exec(points_dict[difficultLevel])
                    user.total_games += 1
                    user.points = sum([user.easy, user.normal * 2, user.hard * 3, user.evil * 4])
            alert_type=2
            flash("Correct! +" + str(difficultLevel) + " point(s)!")
            return render_template(template, table=checkTable, alert_type=alert_type, difficult= difficultText, \
                                   visibleCells = request.form["visibleCells"], hiddenCells=request.form["hiddenCells"])

    else:
        newSudoku = SudokuMaker(difficultLevel)
        table = newSudoku.makeSudoku()
        alert_type = 0
        return render_template(template, table=table, alert_type = alert_type, difficult= difficultText, \
                           visibleCells = newSudoku.getVisible(), hiddenCells= newSudoku.getHidden())

#########################################################################################################

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['SUDOKU_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['SUDOKU_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr= Thread(target = send_async_email, args=[app, msg])
    thr.start()
    return thr

#########################################################################################################

@app.errorhandler(403)
def forbidden(a):
    return render_template("err/403.html"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template("err/404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("err/500.html"), 500

#########################################################################################################

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/easy", methods= ['GET','POST'])
def easy():
    return make_game(1)


@app.route("/normal", methods= ['GET','POST'])
def normal():
    return make_game(2)


@app.route("/hard", methods= ['GET','POST'])
def hard():
    return make_game(3)


@app.route("/evil", methods= ['GET','POST'])
def evil():
    return make_game(4)



@app.route("/register", methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data, \
        username=form.username.data, \
        password=form.password.data)

        db.session.add(user)

        send_email(form.email.data, "Welcome to online Sudoku!", "mail/welcome_user" , \
                   email=form.email.data, password = form.password.data)
        send_email(app.config["SUDOKU_ADMIN"], "New User Registered", "mail/new_user", username=form.username.data)

        flash('You can now login.')
        session["alert_type"] = 2
        return redirect(url_for('login'))
    return render_template("auth/register.html", form=form)



@app.route("/login", methods = ['GET', 'POST'])
def login():
    alert_type = 0
    if "alert_type" in session:
        alert_type = int(session["alert_type"])
        del(session["alert_type"])

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("Welcome, " + user.username + " !")
            session["email"] = form.email.data
            return redirect(url_for("index"))
        else:
            alert_type = 1
            flash("Invalid username or password.")
    return render_template("auth/login.html", form=form, alert_type = alert_type)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route('/user/<name>')
@login_required
def user(name):
    user = User.query.filter_by(email = session["email"]).first()
    firstTen = User.query.order_by(User.points).limit(10)
    return render_template("auth/user.html", current = user, firstTen = firstTen)


if __name__ == "__main__":
    app.run(port=80)




