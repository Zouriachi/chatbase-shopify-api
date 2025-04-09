from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Récupération sécurisée des identifiants via les variables d’environnement
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_PASSWORD = os.getenv("SHOPIFY_ADMIN_TOKEN")
SHOP_NAME = "conedmar"

@app.route("/order-status", methods=["GET"])
def order_status():
    order_number = request.args.get("order_number")
    if not order_number:
        return jsonify({"message": "Merci d’indiquer un numéro de commande."}), 400

    # Shopify exige le préfixe "#"
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

    order = orders[0]  # une seule commande correspond normalement

    # 🎯 Extraction intelligente des infos utiles
    client_info = order.get("customer", {})
    status = order.get("fulfillment_status") or "Non traitée"
    total = order.get("total_price") + " " + order.get("currency")
    name = order.get("name", "")
    items = [line["name"] for line in order.get("line_items", [])]

    return jsonify({
        "commande": name,
        "statut": status,
        "client": f"{client_info.get('first_name', '')} {client_info.get('last_name', '')}".strip(),
        "email": client_info.get("email", ""),
        "total": total,
        "articles": items
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
