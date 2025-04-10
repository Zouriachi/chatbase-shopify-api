
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

SHOPIFY_API_KEY = os.environ.get("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.environ.get("SHOPIFY_API_PASSWORD")
SHOPIFY_STORE_NAME = os.environ.get("SHOPIFY_STORE_NAME")

@app.route("/order-status", methods=["GET"])
def order_status():
    order_number = request.args.get("order_number")
    phone = request.args.get("phone")

    if not order_number:
        return jsonify({"error": "Merci de fournir le numéro de commande"}), 400

    if not order_number.startswith("#"):
        order_number = f"#{order_number}"

    url = f"https://{SHOPIFY_API_KEY}:{SHOPIFY_API_PASSWORD}@{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/orders.json?name={order_number}"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"message": "Commande introuvable. Veuillez vérifier le numéro."}), 404

    data = response.json()
    orders = data.get("orders", [])

    if not orders:
        return jsonify({"message": "Aucune commande trouvée avec ce numéro."}), 404

    order = orders[0]

    # Construction réponse de base
    statut = order.get("fulfillment_status") or "Non traitée"
    message = f"✅ Le statut de votre commande {order_number} est : {statut}."

    # Vérifie si le client demande le numéro de suivi
    if phone:
        phone = phone.replace(" ", "").replace("+", "").replace("-", "")
        client_phone = (order.get("phone") or "").replace(" ", "").replace("+", "").replace("-", "")
        if phone in client_phone:
            tracking_numbers = []
            fulfillments = order.get("fulfillments", [])
            for f in fulfillments:
                tracking_numbers.extend(f.get("tracking_numbers", []))
            if tracking_numbers:
                message += f" 📦 Numéro de suivi : {', '.join(tracking_numbers)}"
            else:
                message += " 📦 La commande a été validée mais aucun numéro de suivi n’est disponible pour le moment."
        else:
            message += " ⚠️ Le numéro de téléphone fourni ne correspond pas à celui utilisé lors de la commande."

    else:
        message += " 📍 Pour obtenir le suivi colis, merci de saisir le téléphone utilisé lors de la commande."

    return jsonify({"message": message})

if __name__ == "__main__":
    app.run(debug=False)
