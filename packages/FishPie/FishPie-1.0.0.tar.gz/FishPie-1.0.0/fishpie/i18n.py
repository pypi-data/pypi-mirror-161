# coding: utf-8

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
import flask_babel

from fishpie import app

babel = flask_babel.Babel(app)
app.jinja_env.globals.update(format_date=flask_babel.format_date)

LANGUAGES = {
    "en": "English",
    "fr": "Français"
}

@babel.localeselector
def get_locale():
    return flask.request.accept_languages.best_match(LANGUAGES.keys())
