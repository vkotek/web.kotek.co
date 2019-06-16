from flask import Blueprint, render_template

page = Blueprint('page', __name__, template_folder='templates')

@page.route("/subscription/admin")
def admin():
    return render_template('page/subscription/admin.html', data=None)
    # users = db.User().users
    #
    # data = {}
    #
    # data['general'] = {'users_count': len(users)}
    # data['restaurants'] = db.Restaurants().restaurants
    # data['users'] = users
    #
    # return render_template('subscription-admin.html', data=data)
