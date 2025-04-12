from flask import Flask
from routes.commandes import commandes_bp

app = Flask(__name__)

# Enregistrement des routes
app.register_blueprint(commandes_bp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
