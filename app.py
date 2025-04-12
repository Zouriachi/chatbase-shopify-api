from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

def normalize_phone(phone):
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, phone))

def get_shopify_order(order_number):
    shop_name = os.environ.get("SHOPIFY_STORE_NAME")
    admin_token = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    
    url = f"https://{shop_name}.myshopify.com/admin/api/2023-10/orders.json?name=#{order_number}"
    headers = {
        "X-Shopify-Access-Token": admin_token,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("orders", [])
    return []

def format_order_response(order):
    number = order.get("name")
    status = order.get("fulfillment_status") or "Non traitée"
    total_price = order.get("total_price")
    customer = order.get("customer", {})
    client_name = customer.get("first_name", "") + " " + customer.get("last_name", "")
    email = customer.get("email", "")

    line_items = [
        f"{item.get('name')}" for item in order.get("line_items", [])
    ]

    shipping_lines = order.get("shipping_lines", [])
    tracking_number = None
    if shipping_lines:
        tracking_info = shipping_lines[0].get("tracking_numbers")
        if tracking_info:
            tracking_number = tracking_info[0]

    return {
        "commande": number,
        "statut": status,
        "total": f"{total_price} MAD",
        "client": client_name,
        "email": email,
        "articles": line_items,
        "tracking_number": tracking_number
    }

@app.route("/order-status", methods=["GET"])
def get_order_status():
    order_number = request.args.get("order_number")
    phone = request.args.get("phone")

    if not order_number:
        return jsonify({"message": "Numéro de commande requis."}), 400

    orders = get_shopify_order(order_number)
    if not orders:
        return jsonify({"message": "Aucune commande trouvée."}), 404

    order = orders[0]

    # Si téléphone fourni, vérifier que ça correspond au client
    if phone:
        client = order.get("customer")
        if not client:
            return jsonify({"message": "Impossible de retrouver le client."}), 404

        client_phone = normalize_phone(client.get("phone", ""))
        input_phone = normalize_phone(phone)

        if client_phone != input_phone:
            return jsonify({"message": "Numéro de téléphone incorrect."}), 403

    response = format_order_response(order)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

