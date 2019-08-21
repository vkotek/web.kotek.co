from flask import Blueprint, render_template

page = Blueprint('page', __name__, template_folder='templates')

@page.route("/")
def admin():
    return render_template('page/home.html', data=None)
