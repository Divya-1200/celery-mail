
'''
source:
https://blog.miguelgrinberg.com/post/using-celery-with-flask 
'''


import random
import time
import os
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from flask_mail import Mail, Message
from celery import Celery

app = Flask(__name__)
app.config['SECRET_KEY'] = 'adichi kepanga apaiyum solla kudathu'

# Flask-Mail configuration
app.config['MAIL_SERVER']           = 'smtp.googlemail.com'
app.config['MAIL_PORT']             = 587
app.config['MAIL_USE_TLS']          = True
#app.config['MAIL_USERNAME']         =
#app.config['MAIL_PASSWORD']         =config('MAIL_PASSWORD')
MAIL_USERNAME="d92079525@gmail.com"
MAIL_PASSWORD="sample-1234"
app.config['MAIL_DEFAULT_SENDER']   ="d92079525@gmail.com"

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_BACKEND'] = 'redis://localhost:6379/0'

# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config) 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    # send the email
    data_email = {
        'subject': 'Celery Check',
        'to': email,
        'body': 'Nan vandhuten nu sollunga'
    }
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(data_email)
        flash('Sending email to {0}'.format(email))
    else:
        # send in one minute
        send_async_email.apply_async(args=[data_email], countdown=60)
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('index'))


@celery.task
def send_async_email(data_email):
    """Background task to send an email with Flask-Mail."""
    msg = Message(data_email['subject'],
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[data_email['to']])
    msg.body = data_email['body']
    with app.app_context():
        mail.send(msg)

if __name__ == '__main__':
    app.run(debug=True)