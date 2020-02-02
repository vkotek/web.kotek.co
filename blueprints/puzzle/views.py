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

puzzle = Blueprint('puzzle', __name__, template_folder='templates', url_prefix='/puzzle')

@puzzle.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        actiontype = request.form['actiontype']
        record(actiontype)

    data = get_info()
    
    return render_template('puzzle/index.html', data=data)

@puzzle.route("/add/", methods=['GET'])
def add():
    record('ADD')
    data = json.dumps(get_info())
    return Response(data, status=200, mimetype='application/json')
    
def record(option):
    with open('counter.txt', 'a+') as f:
        t = dt.datetime.now().timestamp()
        f.write( str(option) + ',' + str(t) + '\n' )
    return None

def get_info():
    with open('counter.txt', 'r+') as f:
        lines = f.readlines()
        lines.reverse()
        
        # Get total count
        count = 0
        for line in lines:
            if 'ADD' in line:
                count += 1
        
        # Get last start/end date
        for line in lines:
            state = line.strip().split(",")
            if state[0] in ['START', 'END']:
                break
                
        time = float( state[1] )
        time_nice = dt.datetime.fromtimestamp(time).strftime("%H:%M:%S")
        
        return {'pieces': count, 'status': state[0], 'time': time ,'time_pretty': time_nice  }
    