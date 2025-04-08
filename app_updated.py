from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SHOPIFY_API_KEY = "votre_api_key"
SHOPIFY_PASSWORD = "votre_mot_de_passe"
SHOP_NAME = "votre_nom_de_boutique.myshopify.com"

@app.route('/order-status', methods=['GET'])
def order_status():
    email = request.args.get('email')
    order_number = request.args.get('order_number')

    if not email and not order_number:
        return jsonify({"error": "Veuillez fournir un email ou un numéro de commande."}), 400

    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}/admin/api/2023-10/orders.json"

    if order_number:
        url += f"?name=#{order_number}"
    elif email:
        url += f"?email={email}"

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Erreur lors de l'accès à Shopify."}), 500

    data = response.json()
    if not data.get("orders"):
        return jsonify({"message": "Aucune commande trouvée."})

    order = data["orders"][0]
    return jsonify({
        "order_number": order["order_number"],
        "status": order["fulfillment_status"],
        "created_at": order["created_at"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
