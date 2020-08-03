from flask import Flask, redirect, url_for, render_template, request, session, flash
import os
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Table, Column, Integer, ForeignKey
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(12)
app.permanet_session_lifetime = timedelta(days=3650)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///followers.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

db = SQLAlchemy(app)

class users(db.Model):
	__tablename__ = 'users'
	_id = db.Column("id", db.Integer, primary_key = True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))

	def __init__(self, name, email):
		self.name = name
		self.email = email

class posts(db.Model):
	__tablename__ = 'posts'
	_id = db.Column("id", db.Integer, primary_key = True)
	creator = db.Column(db.Integer, ForeignKey('users.id'))
	text = db.Column(db.String(500))

	def __init__(self, text, creator):
		self.text = text
		self.creator = creator	

class followers(db.Model):
	__tablename__ = 'followers'
	_id = db.Column("id", db.Integer, primary_key = True)
	follower = db.Column(db.Integer, ForeignKey('users.id'))
	following = db.Column(db.Integer, ForeignKey('users.id'))

	def __init__(self, follower, following):
		self.follower = follower
		self.following = following	

"""
Home Page with Login
"""
def logged_in(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):

		if not "id" in session:
			flash("Please log in")
			return redirect(url_for("home"))
		return f(*args, **kwargs)

	return decorated_function


@app.route("/", methods = ["POST", "GET"])
def home():
	if request.method == "POST":
		session.permananent = True
		email = request.form["email"]
		user = users.query.filter_by(email = email).first()
		if user:
			session["id"] = user._id
			return redirect(url_for("profile", id1 = session["id"])) 
		else:
			flash("Email not Found")
			return render_template("index.html")

	else:
		if "id" in session:
			return redirect(url_for("profile", id1 = session["id"]))
		return render_template("index.html")


"""
Creating a new User
"""
@app.route("/signup", methods = ["POST", "GET"])
def signup():
	if request.method == "POST":
		name = request.form["name"]
		email = request.form["email"]
		if users.query.filter_by(email = email).first():
			flash("User already exists. Please Login.")
			return redirect(url_for("home"))
		else:
			user = users(name, email)
			db.session.add(user)
			db.session.commit()
			flash("User Created. Please Login.")
			return redirect(url_for("home"))
	else:
		return render_template("signup.html")


"""
Logout
"""
@app.route("/logout")
@logged_in
def logout():
	session.pop("id", None)
	return redirect(url_for("home"))




"""
Profile Page
"""
@app.route('/user/<id1>', methods = ["GET", "POST"])
@logged_in
def profile(id1):
	current_user = users.query.get(session["id"])
	i_following1 = followers.query.filter_by(follower=session["id"]).all()
	i_following = [p.following for p in i_following1]
	id2 = int(id1)
	is_following = False
	users1=users.query.all()
	user = users.query.get(id2)
	followers1 = followers.query.filter_by(following=id2).all()
	following1 = followers.query.filter_by(follower=id2).all()
	following = [p.following for p in following1]
	if id2 in i_following:
		is_following = True
	else:
		is_follwowing = False
	following_post = posts.query.filter(posts.creator.in_(following)).all()
	self_post = posts.query.filter_by(creator = id2).all()
	return render_template("profile.html", data = [user, len(followers1), len(following), current_user, is_following], users=users1, posts=following_post, self_p = self_post)


"""
Post Creation
"""
@app.route('/post_new', methods = ["POST", "GET"])
@logged_in
def post():
	post = posts(request.form["body"], session["id"])
	db.session.add(post)
	db.session.commit()
	return redirect(url_for("profile", id1 = session["id"]))


"""
Add followers
"""
@app.route('/followers', methods = ["POST", "GET"])
@logged_in
def follower():
	following = request.form["id"]
	f = followers(session["id"], int(following))
	db.session.add(f)
	db.session.commit()
	return redirect(url_for("profile", id1 = following))

@app.route('/followers_and_following/<id1>', methods = ["POST", "GET"])
@logged_in
def follower_and_following(id1):
	followers1 = followers.query.filter_by(following=id1).all()
	following1 = followers.query.filter_by(follower=id1).all()
	follower = [users.query.get(p.follower) for p in followers1]
	following = [users.query.get(p.following) for p in following1]
	return render_template("follow.html", content = [follower, following])
"""
Edit Profile
"""
@app.route('/edit', methods = ["GET", "POST"])
@logged_in
def edit():
	if request.method == "POST":
		user = users.query.get(session["id"])
		user.name = request.form["name"]
		user.email = request.form["email"]
		db.session.commit()
		flash("Profile Updated")
		return redirect(url_for("profile", id1=session["id"]))
	else:
		user = users.query.get(session["id"])
		return render_template("edit.html", content = [user.name, user.email])



if __name__ == "__main__":
	db.create_all()
	app.run(debug = True)