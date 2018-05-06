import logging

from flask import Blueprint, render_template

from app.flask_utils import login_required

mod_profile = Blueprint('profile', __name__, url_prefix='/profile')


@mod_profile.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    logging.info('profile method')
    return render_template('profile/profile.html', code=200)
