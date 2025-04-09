from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SHOPIFY_API_KEY = "8480b6a17827488c54a88c4625269947"
SHOPIFY_PASSWORD = "508abc1de832ed973abcf5878fd55ee0"
SHOP_NAME = "dwirty.myshopify.com"

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
        url += f"?status=any&email={email}"

    response = requests.get(url)

    try:
        data = response.json()
    except Exception as e:
        return jsonify({
            "error": "Erreur lors de la lecture de la réponse JSON de Shopify",
            "status_code": response.status_code,
            "response_text": response.text
        }), 500

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
