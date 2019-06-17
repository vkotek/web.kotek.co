from flask import (
    Flask,
    flash,
    render_template,
    render_template_string,
    request,
    session,
    redirect,
    url_for,
    g,
    Markup)
from functools import wraps
import json
import hashlib
import csv

from flask_menu import Menu, register_menu
################################################################################
################################# New Format ###################################
################################################################################

def create_app():
    """
    Create the flask app using the new structure and runnable in a container.

    :return: Flask app
    """

    from blueprints.lunchscraper import lunchScraper
    from blueprints.projects import projects
    from blueprints.scrabble import scrabble
    from blueprints.api import api

    app = Flask(__name__, instance_relative_config=True)
    Menu(app=app)

    # app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=True)

    # app.register_blueprint(page)
    app.register_blueprint(lunchScraper)
    app.register_blueprint(projects)
    app.register_blueprint(scrabble)
    app.register_blueprint(api)

    error_templates(app)
    #
    # def tmpl_show_menu():
    #     return render_template_string(
    #     """
    #     {% for item in current_menu.children %}
    #     {% if item.active %}*{% endif %}{{item.text}}
    #     {% endfor %}
    #     """
    #     )
    #
    # @app.route('/menu')
    # @register_menu(app, '.', 'Home')
    # def menu():
    #     return tmpl_show_menu()

    return app
    # return app.run(host='0.0.0.0', port=8888, debug=True)

def error_templates(app):
    """
    Register 0 or more custom error pages (mutates the app passed in).

    :param app: Flask application instance
    :return: None
    """

    def render_status(status):
        """
         Render a custom template for a specific status.
           Source: http://stackoverflow.com/a/30108946

         :param status: Status as a written name
         :type status: str
         :return: None
         """
        # Get the status code from the status, default to a 500 so that we
        # catch all types of errors and treat them as a 500.
        code = getattr(status, 'code', 500)
        return render_template('errors/{0}.html'.format(code)), code

    for error in [404]:
        app.errorhandler(error)(render_status)

    return None

################################################################################
########################## BASIC SITE FUNCTIONS AND PAGES ######################
################################################################################
#
# def tmpl_show_menu():
#     return render_template_string(
#     """
#     {% for item in current_menu.children %}
#     {% if item.active %}*{% endif %}{{item.text}}
#     {% endfor %}
#     """
#     )
#
# @app.route('/menu')
# @register_menu(app, '.', 'Home')
# def menu():
#     return tmpl_show_menu()

#
# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'username' not in session:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function
#
# @app.route("/")
# @login_required
# def index():
#     data = ["Hello"]
#     return render_template('index.html')
#
# @app.route("/login", methods=['GET','POST'])
# def login():
#     if request.method == 'POST':
#         try:
#             user = request.form['username']
#             pw = salt + request.form['password']
#             pw_hashed = hashlib.md5(pw.encode('utf8')).hexdigest()
#             with open('users.csv') as users:
#                 users = csv.reader(users, delimiter=',', quotechar='"')
#                 for u in users:
# #                    print(u, pw_hashed)
#                     if user == u[0] and pw_hashed == u[1]:
#                         flash('Log in successful')
#                         session['username'] = request.form['username']
#                         if request.args.get('next'):
#                             return redirect(request.args.get('next'))
#                         return redirect(url_for('index'))
#         except:
#             flash("Invalid username or password")
#             return redirect(url_for('login'))
#
#     return render_template('login.html')
#
# @app.route("/register", methods=['GET','POST'])
# @login_required
# def register():
#
#     if request.method == 'POST':
#         user = request.form['username']
#         pw = salt + request.form['password']
#         pw_hashed = hashlib.md5(pw.encode('utf8')).hexdigest()
#         with open('users.csv', 'a') as users:
#             users = csv.writer(users, delimiter=',', quotechar='"')
#             users.writerow([user, pw_hashed])
#         flash('User created.')
#         return redirect(url_for('index'))
#
#     elif request.method == 'GET':
#         return render_template('register.html')
#
#     return render_template('login.html')
#
# @app.route("/logout")
# @login_required
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('login'))

################################################################################
########################### HOME AUTOMATION API ################################
################################################################################

# @app.route("/switch/<pin>", methods=['GET'])
# def lights(pin):
#
#     conn = sqlite3.connect(db_file)
#     c = conn.cursor()
#     c.execute('SELECT sensor_name, value FROM sensors WHERE id = ?', pin)
#     state = c.fetchone()
#     if not state:
#         flash('Sensor not found in database.')
#         return redirect(url_for('index'))
# #    print(state)
# #    print(request)
#     args = request.args.get("action", default = 0, type = int)
#
#     if args == 0: # Switch on/off
#         if state[1] == 1:
#             new_state = 0
#         else:
#             new_state = 1
#     elif args == 1: # Decrease value
#         flash('Decreased value')
#         new_state = state[1] - 1
#     elif args == 2: # Increase value
#         flash('Increased value')
#         new_state = state[1] + 1
#     else:
#         flash('Invalid switch action!')
#         return redirect(url_for('index'))
#
#     c.execute('UPDATE sensors SET value = ? WHERE id = ?', (new_state, pin))
#     conn.commit()
#     conn.close()
#
#     flash('Set value {} for {}.'.format(new_state, state[0]))
#     return redirect(url_for('index'))
#
# @app.route("/home", methods=['GET'])
# @login_required
# def home():
#
#     data = {'climate': {} }
#
#     x = room_controls.get_climate_daily()
#     data['climate']['daily'] = \
#         [[','.join([r[0][0], str(int(r[0][1])-1), r[0][2]]),r[1],r[2]] \
#          for r in [[row[1].split('-'), row[2], row[3]] for row in x]]
#
# #    y = room_controls.get_climate()
# #    y['datetime'] = pd.to_datetime(x['time'])
# #    x.index = x['datetime']
# #    data['climate']['hourly'] = x.resample("H").mean()
#
#     return render_template('home.html', data=data)
#
# @app.route("/home/update", methods=['GET','POST'])
# @login_required
# def home_update():
#
#     if room_controls.update_all():
#         flash('Data updated successfully')
#     else:
#         flash('Error updating data')
#
#     return redirect(url_for('home'))

################################################################################
##############################  CRYPTO TRADER ##################################
################################################################################

# @app.route("/trader")
# @login_required
# def trader():
#     f = "/home/vojtech/scripts/botfinex/info.log"
#     try:
#         with open(f, 'r') as f:
#             data = f.readlines()
#             data = data[-50:]
#     except:
#         data = "Cannot get latest trading data."
#     return render_template('trader.html', data=data)
#
# @app.route("/trader/refresh")
# @login_required
# def trader_refresh():
#     drawchart.drawchart()
#     sleep(2)
#     return redirect(url_for('trader'))


################################################################################
##################################### END ######################################
################################################################################

if __name__ == "__main__":
    create_app()
    # app.run(host='0.0.0.0', port=8888, debug=True)
