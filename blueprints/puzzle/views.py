from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    Response,
)
import json
import datetime as dt
import subprocess

puzzle = Blueprint('puzzle', __name__, template_folder='templates', url_prefix='/puzzle')

filename = "counter.txt"

@puzzle.route("/old", methods=['GET','POST'])
def index_old():
    if request.method == 'POST':
        actiontype = request.form['actiontype']
        record(actiontype)

    data = get_info()

    return render_template('puzzle/index_old.html', data=data)

@puzzle.route("/", methods=['GET'])
def index():

    data = get_info()

    return render_template('puzzle/index.html', data=data)

@puzzle.route("/<string:act>/", methods=['GET'])
def action(act):
    act = str(act).upper()
    if act not in ("STA", "END", "ADD"):
        return Response("Invalid Request", status=422)

    record(act)
    # data = json.dumps(get_info())
    data = "OK"
    return Response(data, status=200, mimetype='application/json')

@puzzle.route("/info/", methods=['GET'])
def state():
    info = get_info()
    data = json.dumps(info)
    return Response(data, status=200, mimetype='application/json')


def record(option):
    with open(filename, 'a+') as f:
        t = dt.datetime.now().timestamp()
        t = round(t)
        f.write( str(option) + ';' + str(t) + '\n' )
    return None

def total_time_elapsed():
    return None

def get_info():
    with open(filename, 'r+') as f:
        lines = f.readlines()

        # Get total count
        count = 0
        for line in lines:
            if 'ADD' in line:
                count += 1

        total_seconds = 0
        line_number = 0

        start = None
        for line in lines:
            line_number += 1
            record = line.strip().split(";")
            if record[0] == 'STA':
                start = record[1]
            elif record[0] == 'END':
                try:
                    total_seconds += (float(record[1]) - float(start))
                    start = None
                except:
                    print('Probably an end without a start on line ', line_number)
            else:
                continue

        lines.reverse()

        # Get collected in last session
        last_session = 0
        for line in lines:
            record = line.strip().split(";")[0]
            if record == 'ADD':
                last_session += 1
            elif record == 'STA':
                break

        # Get last start/end date
        for line in lines:
            state = line.strip().split(";")
            if state[0] in ['STA', 'END']:
                break

    time = float( state[1] )
    time_nice = dt.datetime.fromtimestamp(time).strftime("%H:%M:%S")

    time_per_piece = total_seconds / count
    time_remaining = ( 9000 - count ) * time_per_piece

    def duration(seconds):
        return {
            'days': int( seconds // (60*60*24) ),
            'hours': int( ( seconds % (60*60*24) ) // (60*60) ),
            'minutes': int( ( seconds % (60*60) ) // (60) ),
            'seconds': int( seconds % (60*60) ),
        }


    return {
        'pieces': count,
        'status': state[0],
        'time': time ,
        'total_seconds': duration(total_seconds),
        'time_pretty': time_nice,
        'time_per_piece': int(time_per_piece),
        'time_remaining': duration(time_remaining),
        'last_session': last_session,
        'today': 'tbc',
        'recent_sessions': 'tbc',
    }

@puzzle.route("/details/", methods=['GET'])
def get_info_extended():

    sessions = get_sessions()

    # Recent 5 sessions
    recent = sessions[-5:]

    # Today's and Yesterday's time and pieces
    today_date = dt.date.today().isoformat()
    yesterday_date = (dt.date.today() - dt.timedelta(days=1)).isoformat()

    today = {
        'PIECES': 0,
        'DURATION': 0,
    }
    yesterday = {
        'PIECES': 0,
        'DURATION': 0,
    }

    for session in sessions:
        if session['START'][:10] == today_date:
            today['PIECES'] += session['PIECES']
            today['DURATION'] += session['DURATION']
        if session['START'][:10] == yesterday_date:
            yesterday['PIECES'] += session['PIECES']
            yesterday['DURATION'] += session['DURATION']

    data = {
        'recent': recent,
        'today': today,
        'yesterday': yesterday,
    }
    data = json.dumps(data)
    return Response(data, status=200, mimetype='application/json')

def get_sessions():
    with open(filename, 'r+', encoding="utf-8-sig") as f:
        lines = f.readlines()

    sessions = []

    for n, line in enumerate(lines):

        try:
            action, timestamp = line.split(';')

            if action == "STA":
                session = {
                    "START": round(float(timestamp.strip())),
                    "PIECES": 0,
                }
            elif action == "ADD":
                session['PIECES'] += 1
            elif action == "END":
                session["END"] = round(float(timestamp.strip()))
                session["DURATION"] = session["END"] - session["START"]
                session["START"] = dt.datetime.fromtimestamp(session["START"]).strftime("%Y-%m-%d %H:%M:%S")
                session["END"] = dt.datetime.fromtimestamp(session["END"]).strftime("%Y-%m-%d %H:%M:%S")
                sessions += [session]
        except Exception as e:
            print("ERROR: {}\nLINE: {}\nVALUE: {}".format(e, n, line))

    return sessions
