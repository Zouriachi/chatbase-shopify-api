from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "conedmar"

def clean_phone(p):
    return p.replace(" ", "").replace("-", "").replace("+212", "0").replace("212", "0")

@app.route("/order-status", methods=["GET"])
def order_status():
    order_number = request.args.get("order_number")
    phone = request.args.get("phone")

    if not order_number or not phone:
        return jsonify({"error": "Merci de fournir à la fois le numéro de commande et le numéro de téléphone."}), 400

    if not order_number.startswith("#"):
        order_number = f"#{order_number}"

    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-10/orders.json"
    params = {"name": order_number, "status": "any"}
    auth = (SHOPIFY_API_KEY, SHOPIFY_PASSWORD)

    response = requests.get(url, auth=auth, params=params)
    if response.status_code != 200:
        return jsonify({"error": "Erreur de connexion à Shopify."}), 500

    data = response.json()
    orders = data.get("orders", [])
    if not orders:
        return jsonify({"error": "Aucune commande trouvée avec ce numéro."}), 404

    order = orders[0]
    customer = order.get("customer", {})
    phone_in_shopify = customer.get("phone", "") or order.get("shipping_address", {}).get("phone", "")

    if clean_phone(phone) != clean_phone(phone_in_shopify):
        return jsonify({"error": "Le numéro de téléphone ne correspond pas à la commande."}), 403

    statut = order.get("fulfillment_status") or "Non traitée"
    montant_total = f"{order.get('total_price')} {order.get('currency')}"
    produits = [item["name"] for item in order.get("line_items", [])]

    tracking_number = ""
    transporteur = ""
    fulfillments = order.get("fulfillments", [])
    if fulfillments:
        tracking = fulfillments[0]
        tracking_number = tracking.get("tracking_number", "")
        transporteur = tracking.get("tracking_company", "")

    return jsonify({
        "commande": order.get("name", ""),
        "statut": statut,
        "montant_total": montant_total,
        "produits": produits,
        "tracking_number": tracking_number,
        "transporteur": transporteur
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)
