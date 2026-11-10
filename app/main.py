import os

from app import app
from contacts import contacts

app.register_blueprint(contacts)

# starting the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=os.getenv("FLASK_DEBUG", "0") == "1")
