
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()

login_manager=LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if(user!=None):
            flash("You are already registered!")
            return redirect(url_for("login"))
        hashed_password = generate_password_hash(request.form["password"],method='pbkdf2:sha256',salt_length=8)
        new_user = User(email=request.form["email"],
        password=hashed_password,
        name = request.form["name"]
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("secrets"))
    return render_template("register.html")


@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if(user==None):
            flash("That email does not exist, pls try again. ") 
            return redirect(url_for("login"))

        if check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for('secrets'))
        else:
            flash("Incorrect password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html",name=current_user.name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
@login_required
def download():
    return send_from_directory("static/files","cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
