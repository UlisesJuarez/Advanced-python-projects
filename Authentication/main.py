import email
from flask import Flask, render_template, request, url_for, redirect, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

# db.create_all()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=["GET","POST"])
def register():
    if request.method=="POST":

        if User.query.filter_by(email=request.form["email"]).first():
            flash("You've already signed up with that email, login intead!")
            return redirect(url_for("login"))

        new_user=User(
            email=request.form.get("email"),
            password=generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8),
            name=request.form.get("name"),
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for("secrets",name=new_user.name))
    return render_template("register.html",logged_in=current_user.is_authenticated)


@app.route('/login',methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]
        password=request.form["password"]

        user=User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password,password):
                login_user(user)
                return redirect(url_for("secrets",name=user.name))
            else:
                flash("That password is incorrect, please try again!")
                return redirect(url_for("login"))
        else:
            flash("That email doesn't exits, please try again")
            return redirect(url_for("login"))



    return render_template("login.html",logged_in=current_user.is_authenticated)


@app.route('/secrets')
@login_required
def secrets():
    return render_template("secrets.html",name=request.args.get("name"),logged_in=True)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/download')
@login_required
def download():
    return send_file("static/files/cheat_sheet.pdf")


if __name__ == "__main__":
    app.run(debug=True)
