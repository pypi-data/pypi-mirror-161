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

import csv
import datetime
import os
import time

class Entry(object):
    """ A database entry.
    """
    
    fields = [
        "id", "name", "user", "upload_date", "retention", "delete_id",
        "download_count"]
    
    def __init__(
            self, id, name, user, upload_date, retention, delete_id,
            download_count):
        self.id = id
        self.name = name
        self.user = user
        self.upload_date = upload_date
        self.retention = retention
        self.delete_id = delete_id
        self.download_count = download_count

def read(filename):
    """ Read and return the database from the given file. If file does not
        exist, return an empty database.
    """

    db = {}
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as fd:
            reader = csv.DictReader(fd)
            for entry in reader:
                entry["upload_date"] = datetime.datetime.fromtimestamp(
                    int(entry["upload_date"]))
                entry["retention"] = datetime.timedelta(
                    seconds=int(entry["retention"]))
                entry["download_count"] = int(entry["download_count"])
                entry = Entry(**entry)
                
                db[entry.id] = entry
    return db

def write(db, filename):
    """ Write the database to the given file.
    """

    with open(filename, "w", encoding="utf-8") as fd:
        writer = csv.writer(fd)
        writer.writerow(Entry.fields)
        for id, entry in db.items():
            data = [getattr(entry, field) for field in Entry.fields]
            data[Entry.fields.index("upload_date")] = int(
                time.mktime(entry.upload_date.timetuple()))
            data[Entry.fields.index("retention")] = int(
                entry.retention.total_seconds())
            writer.writerow(data)

def cleanup(filename, upload_dir):
    """ Remove all files older than their retention from disk and database.
    """

    now = datetime.datetime.now()

    db = read(filename)
    for id, entry in db.items():
        age = now-entry.upload_date
        if age > entry.retention:
            os.remove(os.path.join(upload_dir, entry.id))
            del db[id]
    write(db, filename)
