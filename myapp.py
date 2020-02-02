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
    from blueprints.puzzle import puzzle
    from blueprints.api import api
    from blueprints.auth import auth
    from blueprints.page import page

    app = Flask(__name__)
    Menu(app=app)

    # app.config.from_object('config.settings')
    app.config.from_pyfile('settings.py', silent=False)

    # app.register_blueprint(page)
    app.register_blueprint(lunchScraper)
    app.register_blueprint(projects)
    app.register_blueprint(scrabble)
    app.register_blueprint(puzzle)
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(page)

    error_templates(app)

    return app


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

if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0', port=9998, debug=True)
