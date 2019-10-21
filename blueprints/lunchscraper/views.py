from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    jsonify)

# from plugins import db
from plugins.login_manager import login_required
from blueprints.lunchscraper import controller

lunchScraper = Blueprint('lunchscraper', __name__, template_folder='templates', url_prefix='/lunch-scraper')

@lunchScraper.route("/", methods=['GET','POST'])
def index():

    if request.method == 'GET':
        return render_template('page/index.html', user=None, hide_menu=True)

    elif request.method == 'POST':

        user = {'email': request.form['email']}

        if controller.User().add(email=user['email']):
            flash('Thank you, activate your subscription by verifying your email.')
        else:
            flash('Seems like this email is already subscribed!')

        return redirect(url_for('lunchscraper.index'))

@lunchScraper.route("/edit", methods=['GET','POST'])
def edit():

    if request.method == 'GET':

        token = request.args.get('token')
        user = controller.User().get(token=token)

        if user:
            data = {}
            data['user'] = user
            data['restaurants'] = controller.Restaurants().restaurants
            for restaurant in data['restaurants']:
                if str(restaurant['id']) in data['user']['preferences']:
                    restaurant['checked'] = 'checked'
            data['language'] = user['language']
        else:
            data = None

        return render_template('page/edit.html', data=data, hide_menu=True)

    elif request.method == 'POST':

        data = request.form

        token = data['token']

        if 'forget' in data:
            # Script to remove user.
            uuid = controller.User().get(token=token)['uuid']
            controller.User().remove(uuid)
            return redirect(url_for('lunchscraper.forgotten'))

        new_preferences = [pref[0] for pref in data.getlist('preferences')]


        user = controller.User()
        # Update preferences
        update_preferences = user.update_preferences(token, new_preferences)
        # Update language
        uuid = user.get(token=token)['uuid']
        update_language = user.update(uuid, 'language', data['language'])

        update = update_preferences and update_preferences

        if update:
            flash("Your preferences have been updated.")
        else:
            flash("There was a problem updating your preferences.")
        return redirect(url_for('lunchscraper.edit', token=token))

@lunchScraper.route("/verify", methods=['GET','POST'])
def verify():
    if request.method == 'GET':
        token = request.args.get('token')
        if controller.User().verify(token):
            user = controller.User().get(token=token)
            flash("The email '{}' has been successfully verified!".format(user['email']))
            text = "Thank you!"
        else:
            flash("There was an issue verifying your email.")
            text = "Oops!"
        return render_template('page/verify.html', text=text, hide_menu=True)
    elif request.method == 'POST':
        # Verify token and mark user as verified.
        return redirect( url_for('lunchscraper.verify'))

@lunchScraper.route("/admin")
@login_required
def admin():

    users = controller.User().users

    data = {}

    data['general'] = {'users_count': len(users)}
    data['restaurants'] = controller.Restaurants().restaurants
    data['users'] = users
    data['notices'] = controller.Email.get_notices()

    return render_template('page/admin.html', data=data)

@lunchScraper.route("/admin/notices", methods=['GET','POST'])
@login_required
def admin_notices():

    if request.method == "POST":
        data = request.form
        result = controller.Email.add_notice(data)
        flash(result)
        return redirect(url_for('lunchscraper.admin'))
    else:
        notices = controller.Email.get_notices()
        return jsonify(notices)

# return render_template('page/admin.html', data=data)

@lunchScraper.route("/menu")
def menu():

    data = controller.Menu.get()

    return render_template('page/menu.html', data=data)

@lunchScraper.route("/forgotten")
def forgotten():
    return render_template('page/forgotten.html')
