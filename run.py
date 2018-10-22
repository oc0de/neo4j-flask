from blog import app
import os

app.secret_key = os.urandom(24)
port = int(os.environ['PORT'])

app.run(host='0.0.0.0', port=port)
