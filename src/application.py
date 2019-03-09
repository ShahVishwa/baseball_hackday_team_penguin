from subprocess import PIPE, Popen
from flask import Flask, render_template, request, url_for, make_response, redirect, g, session, flash, abort
import sqlite3
import json
import jinja2
import os
import sys
import re
import copy
import datetime
import hashlib
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
###
app = Flask(__name__)  # Create Flask Application
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # WHY IS THIS HERE??
app.secret_key = os.urandom(16)


def get_program_std_output(str):
    return Popen([str], stdout=PIPE, shell=True).communicate()[0]


#  This function is used to determine if the current user has signed in user credentials and returns credential information if exists
def check_authorization():
    if session.get('auth') is None:
        return "user"
    else:
        return session.get('auth')


# This route gets called when a user invites another user to manage the web app.
# This function generates and sends the invite over email, and then creates an entry in the invited_users table.
@app.route("/send_email", methods=['POST'])
def send_email():
    if request.form['email'].endswith("@teradata.com") is False:
        flash("Can only invite teradata email accounts")
        return redirect(request.referrer)

    if request.form['account_type_new_user'] not in ['Editor', 'Admin']:
        flash("Invalid")
        return redirect(request.referrer)
        # abort(404)

    # Construct Email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Invitation to edit Teradata OTB Matrix"
    msg['From'] = "td.product.info@gmail.com"
    msg['To'] = request.form['email']

    # Get account info to be put into invited_users database table
    username = request.form['email'][:-13]
    print("printing user" + username)
    account_type = request.form['account_type_new_user']
    print("printing acount type" + account_type)
    # Generate a random key for this user
    random_bytes = os.urandom(64)
    token = base64.b64encode(random_bytes).decode('utf-8')
    token = token.replace("/", "")  # Need to remove all instances of "/" for valid url
    link = request.url_root + "new_user/" + token
    # Create the body of the message (a plain-text and an HTML version).
    text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"
    html = """\
    <html>
        <head></head>
        <body>
            <p>You have been invited to be an {} for the BAR/DSA Product Release Info Page.<br>
            Please click the link below to register!<br>
            This link will only last for 24 hours after being sent.<br>
            {}
            </p>
        </body>
    </html>
    """.format(request.form['account_type_new_user'], link)

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    # Send the message via local SMTP server
    try:
        with sqlite3.connect("./database.db") as con:
            cur = con.cursor()

            s = smtplib.SMTP('smtp.teradata.com', 587)
            s.ehlo()
            s.starttls()
            s.login('ashton.shears@teradata.com', '')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(msg['From'], msg['To'], msg.as_string())
            s.quit()
            cur.execute("INSERT or REPLACE INTO invited_users (id, username, random_number, user_type) VALUES (null,?,?,?)", (username, token, account_type))
            con.commit()
    except Exception as ex:
        flash(ex)
    return redirect(request.referrer)


@app.route("/try_login", methods=['POST'])
def try_login():
    if request.method == 'POST':
        user_entry = request.form['username']
        pass_entry = request.form['password'].encode()
        # Generate a sha256 hash of the password. The database never sees the real password
        pass_hash = hashlib.sha256(pass_entry).hexdigest()
        try_login_with_credentials(user_entry, pass_hash)  # Will sign the user in if credentials are valid.
    return redirect(request.referrer)


def try_login_with_credentials(user, passw):
    with sqlite3.connect("./database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", (user, passw))
        login_result = cur.fetchone()
        if login_result is None:
            flash('Invalid credentials')
        if login_result is not None:
            flash('You were successfully logged in')
            session['username'] = login_result[1]
            session['auth'] = login_result[3]


# This route gets called when a user is trying to register a new account.
# Only accessible if the user has been invited.
@app.route("/submit_new_user", methods=['POST'])
def registration_page_submit():
    with sqlite3.connect("./database.db") as con:
        cur = con.cursor()

        cur.execute("SELECT * FROM invited_users WHERE username = ? AND random_number = ?", (request.form['username'], request.form['random_number']))
        new_user = cur.fetchone()
        if new_user is None:
            flash("Invalid username")
            return redirect(request.referrer)
        # Check if password satisfies requirements
        elif len(request.form['password']) < 8:
            flash("Password length must be at least 8 characters")
            return redirect(request.referrer)
        elif request.form['password'].isalpha():
            flash("Password must contain special characters")
            return redirect(request.referrer)
        elif request.form['password'] != request.form['re-enter-pass']:
            flash("Password entries do not match")
            return redirect(request.referrer)
        flash("success")
        cur.execute("INSERT INTO users (id, us)")
        return render_template("index.html")


# The homepage
@app.route("/")
def main_view_page():
    product_info = 'Test'
    return render_template("index.html", product_info=product_info)


if __name__ == "__main__":
    global will_backup_on_change
    will_backup_on_change = 1  # If 1, will backup on every change.
    # init_db()
    app.run(host='0.0.0.0', port=5000)
