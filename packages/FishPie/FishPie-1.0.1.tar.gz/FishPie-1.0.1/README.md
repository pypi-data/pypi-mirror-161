# Fishpie

Fishpie is web application for sharing large files.

## Installation

Get the package from PyPI:

```bash
python3 -m pip install fishpie
```

Create a WSGI wrapper script:

```python
import datetime

import fishpie
import fishpie.wordpress

app = fishpie.app
app.secret_key = "SOME_VERY_SECRET_BINARY_DATA"
app.permanent_session_lifetime = datetime.timedelta(days=1)
app.config["DATABASE"] = "/my/root/directory/database"
app.config["UPLOAD_DIR"] = "/my/root/directory/uploads"
app.config["authenticate"] = fishpie.wordpress.authenticate
app.config["authentication_data"] = ("host", "user", "password", "database")
app.debug = True

application = app
```

Configure Apache:

```apache
WSGIScriptAlias /transfer /somewhere/fishpie.wsgi
<Directory /somewhere>
  Require all granted
</Directory>
```
