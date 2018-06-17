from flask import render_template, flash, redirect, url_for, jsonify
from app import app			#FROM INIT.PY
from app.forms import LoginForm #FROM /app/forms.py get LoginForm instance
from flask_login import current_user, login_user
from flask_login import logout_user
from flask_login import login_required
from app.models import User
from flask import request
from werkzeug.urls import url_parse
from app import app, db
from app.forms import RegistrationForm
from app.forms import EditProfileForm


#HOME PAGE
@app.route('/')
@app.route('/index')
@login_required
def index():
    users = User.query.all()
    return render_template('index.html', title='Home', users=users)

#LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

#LOGOUT
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

#REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, title=form.title.data, username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#PROFILE
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)

#EDIT PROFILE
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
    	current_user.first_name = form.first_name.data
    	current_user.last_name = form.last_name.data
    	current_user.title = form.title.data
    	current_user.username = form.username.data
    	current_user.email = form.email.data
    	current_user.about_me = form.about_me.data
    	current_user.set_password(form.password.data)
    	db.session.commit()
    	flash('Your changes have been saved.')
    	return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
    	form.first_name.data = current_user.first_name
    	form.last_name.data = current_user.last_name
    	form.title.data = current_user.title
    	form.username.data = current_user.username
    	form.email.data = current_user.email
    	form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
