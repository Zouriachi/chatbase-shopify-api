from flask import Flask
from routes import orders
from routes import products

app = Flask(__name__)

# Enregistrement des blueprints
app.register_blueprint(orders.order_bp)
app.register_blueprint(products.products_bp)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

