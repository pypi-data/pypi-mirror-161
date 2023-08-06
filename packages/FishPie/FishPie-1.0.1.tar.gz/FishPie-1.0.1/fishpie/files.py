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

import datetime
import os
import uuid

import flask

from . import database
from fishpie import app

@app.route("/upload", methods=["POST"])
def upload():
    message = ""
    file = flask.request.files["file"]
    
    retention = flask.request.form.get("retention", 30)
    try:
        retention = datetime.timedelta(days=int(retention))
    except:
        retention = datetime.timedelta(days=30)
    
    if file:
        db = database.read(app.config["DATABASE"])

        # Save the original name in the database
        name = file.filename
        id = uuid.uuid4().hex
        delete_id = uuid.uuid4().hex
        db[id] = database.Entry(id, name, flask.session["user"], 
            datetime.datetime.now(), retention, delete_id, 0)
        database.write(db, app.config["DATABASE"])

        file.save(os.path.join(app.config["UPLOAD_DIR"], id))
    
    return ""

@app.route("/<id>")
def download(id):
    database.cleanup(app.config["DATABASE"], app.config["UPLOAD_DIR"])

    if not os.path.isfile(os.path.join(app.config["UPLOAD_DIR"], id)):
        flask.abort(404)
    
    # Fetch the original name from the database
    db = database.read(app.config["DATABASE"])
    if id not in db:
        flask.abort(404)

    db[id].download_count += 1
    database.write(db, app.config["DATABASE"])
    
    # Serve the file with its original name
    return flask.send_from_directory(app.config["UPLOAD_DIR"], id, 
        as_attachment=True, attachment_filename=db[id].name)

@app.route("/delete/<delete_id>")
def delete(delete_id):
    db = database.read(app.config["DATABASE"])
    files = [
        (key, value) for key, value in db.items() if value.delete_id==delete_id]
    if not files:
        flask.abort(404)
    if len(files)>1:
        flask.abort(500)

    os.remove(os.path.join(app.config["UPLOAD_DIR"], files[0][0]))
    del db[files[0][0]]

    database.write(db, app.config["DATABASE"])

    return flask.render_template("delete.html", original_name=files[0][1].name)
