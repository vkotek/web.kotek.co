from flask import (
    Blueprint,
    render_template,
    request,
    flash,
)

import datetime, time

from plugins import scrabbler

scrabble = Blueprint('scrabble', __name__, template_folder='templates', url_prefix='/scrabble')

################################################################################
############################## SCRABBLE PAGES ##################################
################################################################################

@scrabble.route("/", methods=['GET','POST'])
# @login_required
def index():
	if request.method == 'POST':
		letters = request.form['letters']
		length = int(request.form['length'])
		s = scrabbler()
		data = s.words_top(s.words_scored(s.words_from(letters, length)))
	else:
		data = None
	return render_template('scrabble/index.html', data=data)

@scrabble.route("/history", methods=['GET','POST'])
# @login_required
def history():
    data = {}
    data['games'] = scrabbler.get_games()
    data['timestamp'] = str(round(time.time()))
    if request.args.get('game'):
        game = request.args.get('game')
        data['game'] = scrabbler.get_game(game)
    return render_template('scrabble/history.html', data=data)

@scrabble.route("/insert", methods=['GET','POST'])
# @login_required
def insert():
    if request.method == 'GET':
        data = {
            'game_id': scrabbler.get_last_game_id(),
            'date': str(datetime.date.today()),
        }
        return render_template('scrabble/insert.html', data=data)

    elif request.method == 'POST':
        print("Posting data..")
        data = scrabbler.data_parse(request.form)
        print("Trying to insert data..")
        insert = scrabbler.database_insert(data)

        flash('New game data inserted!')

        return redirect(url_for('insert'))

@scrabble.route("/history/update", methods=['GET'])
# @login_required
def update():
    scrabbler.update_graphs()
    return redirect(url_for('history'))
