import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'success')
    return redirect(url_for('auth.login'))


def send_reset_email(user, reset_url):
    mail_address = current_app.config.get('MAIL_ADDRESS')
    mail_password = current_app.config.get('MAIL_APP_PASSWORD')

    if not mail_address or not mail_password:
        current_app.logger.error('MAIL_ADDRESS / MAIL_APP_PASSWORD not configured.')
        return False

    body = (
        f"Hello,\n\n"
        f"A password reset was requested for your Levvi's Furniture admin account.\n\n"
        f"Click the link below to set a new password. This link expires in 1 hour.\n\n"
        f"{reset_url}\n\n"
        f"If you didn't request this, you can safely ignore this email."
    )

    msg = MIMEText(body)
    msg['Subject'] = "Reset your Levvi's Furniture admin password"
    msg['From'] = mail_address
    msg['To'] = user.email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(mail_address, mail_password)
            server.sendmail(mail_address, user.email, msg.as_string())
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send reset email: {e}')
        return False


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        user = User.query.filter_by(username=username).first()

        if user and user.email:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()

            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_reset_email(user, reset_url)

        # Always show the same message, whether or not the username/email
        # actually matched anything — this avoids revealing which usernames
        # exist to anyone probing the form.
        flash('If that account exists and has an email on file, a reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.reset_token_expiry or user.reset_token_expiry < datetime.utcnow():
        flash('That reset link is invalid or has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not new_password or len(new_password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Your password has been reset. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)