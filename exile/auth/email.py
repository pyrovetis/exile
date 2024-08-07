from flask import render_template, current_app

from exile.email import send_email


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        "[EXILE] Reset Your Password",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template("email/reset-password.txt", user=user, token=token),
        html_body=render_template("email/reset-password.html", user=user, token=token),
    )
