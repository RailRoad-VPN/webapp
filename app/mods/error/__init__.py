from http import HTTPStatus

from flask import render_template


def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error/not_found.html'), HTTPStatus.NOT_FOUND


def forbidden(e):
    # note that we set the 404 status explicitly
    return render_template('error/forbidden.html'), HTTPStatus.FORBIDDEN


def internal_server_error(e):
    # note that we set the 404 status explicitly
    return render_template('error/internal_server_error.html'), HTTPStatus.INTERNAL_SERVER_ERROR
