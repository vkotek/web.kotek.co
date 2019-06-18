from flask import (
    Blueprint,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    session,
)

from plugins.login_manager import login_required

auth = Blueprint('auth', __name__, template_folder='templates', url_prefix='/auth')


@auth.route("/")
@login_required
def index():
    data = ["Hello"]
    return render_template('index.html')

@auth.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        try:
            user = request.form['username']
            pw = salt + request.form['password']
            pw_hashed = hashlib.md5(pw.encode('utf8')).hexdigest()
            with open('users.csv') as users:
                users = csv.reader(users, delimiter=',', quotechar='"')
                for u in users:
#                    print(u, pw_hashed)
                    if user == u[0] and pw_hashed == u[1]:
                        flash('Log in successful')
                        session['username'] = request.form['username']
                        if request.args.get('next'):
                            return redirect(request.args.get('next'))
                        return redirect(url_for('auth.index'))
        except:
            flash("Invalid username or password")
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route("/register", methods=['GET','POST'])
@login_required
def register():

    if request.method == 'POST':
        user = request.form['username']
        pw = salt + request.form['password']
        pw_hashed = hashlib.md5(pw.encode('utf8')).hexdigest()
        with open('users.csv', 'a') as users:
            users = csv.writer(users, delimiter=',', quotechar='"')
            users.writerow([user, pw_hashed])
        flash('User created.')
        return redirect(url_for('auth.index'))

    elif request.method == 'GET':
        return render_template('register.html')

    return render_template('login.html')

@auth.route("/logout")
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))
