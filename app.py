from flask import Flask, request, jsonify
import requests
import urllib.parse

app = Flask(__name__)

SHOPIFY_API_KEY = "votre_api_key"
SHOPIFY_PASSWORD = "votre_mot_de_passe"
SHOP_NAME = "votre_nom_de_boutique.myshopify.com"

@app.route('/order-status', methods=['GET'])
def order_status():
    order_number = request.args.get('order_number')

    if not order_number:
        return jsonify({"error": "Veuillez fournir un numéro de commande."}), 400

    # Ajouter # si absent
    if not order_number.startswith("#"):
        order_number = f"#{order_number}"

    # Encoder le # proprement
    encoded_order_number = urllib.parse.quote(order_number)
    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_PASSWORD}@{SHOP_NAME}/admin/api/2023-10/orders.json?name={encoded_order_number}"

    response = requests.get(url)

    try:
        data = response.json()
    except Exception as e:
        return jsonify({
            "error": "Erreur lors de la lecture de la réponse de Shopify",
            "status_code": response.status_code,
            "response_text": response.text
        }), 500

    if not data.get("orders"):
        return jsonify({"message": "Aucune commande trouvée avec ce numéro."})

    order = data["orders"][0]
    return jsonify({
        "order_number": order["order_number"],
        "status": order["fulfillment_status"],
        "created_at": order["created_at"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
