import sys

from blog import app
import os

app.secret_key = os.urandom(24)
# port = int(os.environ.get("PORT", 5000))
port = sys.argv[1]
app.run(host='0.0.0.0', port=port)
