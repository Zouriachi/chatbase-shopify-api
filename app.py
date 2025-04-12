
import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")
SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN
}


def get_order_by_name(order_number):
    url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/orders.json?name=%23{order_number}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        orders = response.json().get("orders", [])
        return orders[0] if orders else None
    return None


@app.route("/order-status", methods=["GET"])
def get_order_status():
    order_number = request.args.get("order_number")

    if not order_number:
        return jsonify({"error": "Numéro de commande requis."}), 400

    order = get_order_by_name(order_number)
    if not order:
        return jsonify({"message": "Aucune commande trouvée avec ce numéro."}), 404

    # Détails de la commande
    statut = order.get("fulfillment_status", "Non traitée") or "Non traitée"
    total_price = order.get("total_price") + " " + order.get("currency", "")
    line_items = order.get("line_items", [])
    articles = [f"{item['name']}" for item in line_items]
    tracking_numbers = []

    for fulfillment in order.get("fulfillments", []):
        for tracking_number in fulfillment.get("tracking_numbers", []):
            tracking_numbers.append(tracking_number)

    return jsonify({
        "commande": order.get("name"),
        "statut": statut,
        "total": total_price,
        "articles": articles,
        "tracking": tracking_numbers
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
