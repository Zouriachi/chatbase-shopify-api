from flask import Flask
from routes import orders
from routes import products
from routes import product_info
app = Flask(__name__)

# Enregistrement des blueprints
app.register_blueprint(orders.order_bp)
app.register_blueprint(products.products_bp)
app.register_blueprint(product_info.product_info_bp)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)


