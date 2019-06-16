from flask import (
    Blueprint,
    render_template,
    request,
    flash)

from plugins import db

lunchScraper = Blueprint('lunchscraper', __name__, template_folder='templates', url_prefix='/lunch-scraper')

# @lunchScraper.route("/admin")
# def admin():
#     return render_template('page/admin.html', data=None)
    # users = db.User().users
    #
    # data = {}
    #
    # data['general'] = {'users_count': len(users)}
    # data['restaurants'] = db.Restaurants().restaurants
    # data['users'] = users
    #
    # return render_template('subscription-admin.html', data=data)

@lunchScraper.route("/", methods=['GET','POST'])
def index():

    if request.method == 'GET':
        return render_template('subscription.html', user=None, hide_menu=True)

    elif request.method == 'POST':

        user = {'email': request.form['email']}

        if db.User().add(email=user['email']):
            flash('Thank you, activate your subscription by verifying your email.')
        else:
            flash('Seems like this email is already subscribed!')

        return redirect(url_for('index'))

@lunchScraper.route("/edit", methods=['GET','POST'])
def edit():

    if request.method == 'GET':

        token = request.args.get('token')
        user = db.User().get(token=token)

        if user:
            data = {}
            data['user'] = user
            data['restaurants'] = db.Restaurants().restaurants
            for restaurant in data['restaurants']:
                if str(restaurant['id']) in data['user']['preferences']:
                    restaurant['checked'] = 'checked'
        else:
            data = None

        return render_template('page/edit.html', data=data, hide_menu=True)

    elif request.method == 'POST':

        data = request.form

        token = data['token']

        if 'forget' in data:
            # Script to remove user.
            uuid = db.User().get(token=token)['uuid']
            db.User().remove(uuid)
            flash("Hi.. wait, who is this?")
            return redirect(url_for('subscription_forgotten'))

        new_preferences = [pref[0] for pref in data.getlist('preferences')]
        update = db.User().update_preferences(token, new_preferences)
        if update:
            flash("Your preferences have been updated.")
        else:
            flash("There was a problem updating your preferences.")
        return redirect(url_for('edit', token=token))

@lunchScraper.route("/verify", methods=['GET','POST'])
def verify():
    if request.method == 'GET':
        token = request.args.get('token')
        if db.User().verify(token):
            user = db.User().get(token=token)
            flash("The email '{}' has been successfully verified!".format(user['email']))
            text = "Thank you!"
        else:
            flash("There was an issue verifying your email.")
            text = "Oops!"
        return render_template('page/verify.html', text=text, hide_menu=True)
    elif request.method == 'POST':
        # Verify token and mark user as verified.
        return redirect( url_for('verify'))

@lunchScraper.route("/admin")
# @login_required
def admin():

    users = db.User().users

    data = {}

    data['general'] = {'users_count': len(users)}
    data['restaurants'] = db.Restaurants().restaurants
    data['users'] = users

    return render_template('page/admin.html', data=data)

@lunchScraper.route("/forgotten")
def forgotten():
    return render_template('page/forgotten.html')
