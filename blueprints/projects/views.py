from flask import (
    Blueprint,
    render_template,
    request,
    flash)


projects = Blueprint('projects', __name__, template_folder='templates', url_prefix='/projects')

@projects.route("/ascii", methods=['GET','POST'])
#@login_required
def ascii():
    return "This is the ASCII project."
    # if request.method == 'GET':
    #     data = {}
    #     image_ascii = "/home/vojtech/api.kotek.co/myapp/plugins/img2char/test.html"
    #     with open(image_ascii, 'r') as x:
    #         data['image'] = Markup(x.read())
    #     return render_template('ascii.html', data=data)
    # else:
    #     print('processing image..')
    #     return redirect(url_for('page_ascii'))
