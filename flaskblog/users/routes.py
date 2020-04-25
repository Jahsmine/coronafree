from flask import Blueprint, render_template, url_for, flash, redirect, request
from flaskblog import db, bcrypt
from flaskblog.models import UserModel, PostModel
from flaskblog.users.forms import (
    RegistrationFormModel,
    LoginFormModel,
    UpdateAccountFormModel,
    RequestResetFormModel,
    ResetPasswordFormModel
)
from flask_login import login_user, logout_user, current_user, login_required
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationFormModel()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = UserModel(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginFormModel()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check eamil and password!', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout/")
def logout():
    logout_user()
    flash('To See Content Please Log In ', 'info')
    return redirect(url_for('users.login'))


@users.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountFormModel()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your Account Has Been Updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template(
        'account.html',
        title='Account',
        image_file=image_file,
        form=form
    )


@users.route('/user/<string:username>')
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = UserModel.query.filter_by(username=username).first_or_404()
    posts = PostModel.query.filter_by(author=user)\
        .order_by(PostModel.date_posted.desc())\
        .paginate(per_page=5, page=page)
    return render_template('user_post.html', posts=posts, user=user)


@users.route("/reset_password/", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetFormModel()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been send with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = UserModel.verify_reset_token(token)
    if user is None:
        flash("That is an invalid token or expired token", 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordFormModel()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
