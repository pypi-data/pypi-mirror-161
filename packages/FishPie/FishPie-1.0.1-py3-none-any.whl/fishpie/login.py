# This file is part of Fishpie.
#
# Fishpie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Fishpie is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Fishpie.  If not, see <http://www.gnu.org/licenses/>.

import flask

from . import database
from fishpie import app

@app.route("/login", methods=["GET", "POST"])
def login():
    database.cleanup(app.config["DATABASE"], app.config["UPLOAD_DIR"])
    if flask.request.method == "GET":
        result = flask.render_template("login.html")
    else:
        user = flask.request.form["user"]
        password = flask.request.form["password"]
        authenticated = app.config["authenticate"](
            user, password, *app.config["authentication_data"])
        if authenticated:
            flask.session["user"] = user
            destination = "index"
        else:
            destination = "login"
        result = flask.redirect(flask.url_for(destination, _external=True))

    return result

@app.route("/logout")
def logout():
    flask.session.pop("user", None)
    return flask.redirect(flask.url_for("index"))
