
from flask import Flask, request, jsonify
import requests
import os
from urllib.parse import unquote

app = Flask(__name__)

SHOPIFY_ADMIN_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOPIFY_API_KEY = os.environ.get("SHOPIFY_API_KEY")
SHOPIFY_STORE_NAME = os.environ.get("SHOPIFY_STORE_NAME")
SHOPIFY_API_VERSION = "2023-10"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN
}

def normalize_phone(phone):
    phone = ''.join(filter(str.isdigit, phone))  # Remove non-digits
    if phone.startswith('0'):
        phone = '+212' + phone[1:]
    elif phone.startswith('212'):
        phone = '+212' + phone[3:]
    elif not phone.startswith('+'):
        phone = '+' + phone
    return phone

@app.route("/order-status", methods=["GET"])
def get_order_status():
    order_number = unquote(request.args.get("order_number", ""))
    phone = unquote(request.args.get("phone", ""))

    if not order_number:
        return jsonify({"error": "order_number is required"}), 400

    if not order_number.startswith("#"):
        order_number = f"#{order_number}"

    url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/{SHOPIFY_API_VERSION}/orders.json?name={order_number}"

    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch order data"}), response.status_code

    orders = response.json().get("orders", [])
    if not orders:
        return jsonify({"message": "Aucune commande trouvée avec ce numéro."}), 200

    order = orders[0]
    statut = order.get("fulfillment_status", "Non traitée") or "Non traitée"
    client = order.get("customer", {})
    client_phone = normalize_phone(client.get("phone", ""))
    articles = [line.get("name", "") for line in order.get("line_items", [])]
    total = order.get("total_price", "0.00")
    tracking_info = ""

    if order.get("fulfillments"):
        fulfillment = order["fulfillments"][0]
        tracking_info = fulfillment.get("tracking_number", "")

    if phone:
        phone = normalize_phone(phone)
        if phone == client_phone:
            return jsonify({
                "commande": order_number,
                "statut": statut,
                "client": f"{client.get('first_name', '')} {client.get('last_name', '')}",
                "email": client.get("email", ""),
                "articles": articles,
                "total": f"{total} MAD",
                "suivi": tracking_info
            })
        else:
            return jsonify({"error": "Le numéro de téléphone ne correspond pas à la commande."}), 403

    return jsonify({
        "commande": order_number,
        "statut": statut,
        "suivi": tracking_info,
        "message": "📍 Pour obtenir plus de détails ou le suivi du colis, merci de saisir le téléphone utilisé lors de la commande."
    })

if __name__ == "__main__":
    app.run(debug=False)
