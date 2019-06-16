from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    flash)

import sqlite3
db_file = 'database.db'
# This should be in the model rather than the view...

api = Blueprint('api', __name__, template_folder='templates', url_prefix='/api')

@api.route("/")
def index():
    return render_template("api/index.html")

@api.route("/switch/<pin>", methods=['GET'])
def switch(pin):

    # TO DO: Move this to the model
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('SELECT sensor_name, value FROM sensors WHERE id = {}'.format(pin))
    state = c.fetchone()

    if not state:
        return 'Sensor not found in database.'
        # return redirect(url_for('api.index'))

    args = request.args.get("action", default = 0, type = int)

    if args == 0: # Switch on/off
        if state[1] == 1:
            new_state = 0
        else:
            new_state = 1
    elif args == 1: # Decrease value
        flash('Decreased value')
        new_state = state[1] - 1
    elif args == 2: # Increase value
        flash('Increased value')
        new_state = state[1] + 1
    else:
        flash('Invalid switch action!')
        return redirect(url_for('api.index'))

    c.execute('UPDATE sensors SET value = {} WHERE id = {}'.format(new_state, pin))
    conn.commit()
    conn.close()

    flash('Set value {} for {}.'.format(new_state, state[0]))
    return redirect(url_for('api.index'))

@api.route("/home", methods=['GET'])
# @login_required
def home():

    data = {'climate': {} }

    x = room_controls.get_climate_daily()
    data['climate']['daily'] = \
        [[','.join([r[0][0], str(int(r[0][1])-1), r[0][2]]),r[1],r[2]] \
         for r in [[row[1].split('-'), row[2], row[3]] for row in x]]

    return render_template('home.html', data=data)

@api.route("/home/update", methods=['GET','POST'])
# @login_required
def home_update():

    if room_controls.update_all():
        flash('Data updated successfully')
    else:
        flash('Error updating data')

    return redirect(url_for('api.home'))
