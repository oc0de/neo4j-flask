from blog import app
import os

app.secret_key = os.urandom(24)
port = process.env.PORT || 5000
app.run(host='0.0.0.0', port=port)
