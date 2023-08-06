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

@app.route("/")
def index():
    database.cleanup(app.config["DATABASE"], app.config["UPLOAD_DIR"])

    if "user" not in flask.session:
        return flask.redirect(flask.url_for("login", _external=True))
        
    db = database.read(app.config["DATABASE"])
    files = [x for x in db.values() if x.user == flask.session["user"]]
    files.sort(key=lambda x:x.upload_date)
    
    return flask.render_template("index.html", files=files)
