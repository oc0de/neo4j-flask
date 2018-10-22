from blog import app
import os

app.secret_key = os.urandom(24)
port = os.environ.get('PORT', 5000)
print(port)
app.run(host='0.0.0.0', port=port)
