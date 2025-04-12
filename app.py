from flask import Flask
from routes import all_routes

app = Flask(__name__)

for route in all_routes:
    app.register_blueprint(route)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
