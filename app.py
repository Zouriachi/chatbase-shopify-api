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
    phone = request.args.get("phone")  # facultatif

    if not order_number:
        return jsonify({"message": "Merci d’indiquer un numéro de commande."}), 400

    if not order_number.startswith("#"):
        order_number = f"#{order_number}"

    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/2023-10/orders.json"
    params = {"name": order_number, "status": "any"}
    auth = (SHOPIFY_API_KEY, SHOPIFY_PASSWORD)

    response = requests.get(url, auth=auth, params=params)
    if response.status_code != 200:
        return jsonify({"message": "Erreur de connexion à Shopify."}), 500

    data = response.json()
    orders = data.get("orders", [])
    if not orders:
        return jsonify({"message": "Aucune commande trouvée avec ce numéro."}), 404

    order = orders[0]
    status = order.get("fulfillment_status") or "Non traitée"
    name = order.get("name", "")
    phone_in_shopify = order.get("customer", {}).get("phone", "")
    tracking_info = ""

    # Si téléphone fourni et correspond
    if phone and clean_phone(phone) == clean_phone(phone_in_shopify):
        fulfillments = order.get("fulfillments", [])
        if fulfillments and fulfillments[0].get("tracking_number"):
            tracking = fulfillments[0]
            tracking_info = (
                f"
📍 Suivi : {tracking['tracking_number']} "
                f"({tracking.get('tracking_company', 'transporteur inconnu')})"
            )
        else:
            tracking_info = "
ℹ️ Aucun numéro de suivi disponible pour le moment."
    elif phone:
        tracking_info = "
⚠️ Le numéro de téléphone fourni ne correspond pas à la commande."
    else:
        tracking_info = "
📍 Pour obtenir le suivi colis, merci de saisir le téléphone utilisé lors de la commande."

    message = (
        f"✅ Le statut de votre commande {name} est : {status}.{tracking_info}"
    )

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
