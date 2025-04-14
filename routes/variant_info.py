import os
import requests
from flask import Blueprint, request, jsonify

variant_info_bp = Blueprint("variant_info", __name__)

SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")
SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN
}

def clean(text):
    return text.lower().replace(" ", "").replace("cm", "").strip()

@variant_info_bp.route("/variant_info", methods=["GET"])
def get_variant_info():
    handle = request.args.get("handle")
    variant_label = request.args.get("variant_label")

    if not handle or not variant_label:
        return jsonify({"error": "handle et variant_label requis"}), 400

    try:
        url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json?handle={handle}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        products = data.get("products", [])
        if not products:
            return jsonify({"error": "Produit non trouvé"}), 404

        produit = products[0]
        cleaned_label = clean(variant_label)

        for variant in produit.get("variants", []):
            if cleaned_label in clean(variant.get("title", "")):
                return jsonify({
                    "produit": produit.get("title"),
                    "variante": variant.get("title"),
                    "prix": variant.get("price") + " MAD",
                    "disponible": variant.get("inventory_quantity", 0) > 0,
                    "variant_id": variant.get("id"),
                    "lien_complet": f"https://www.dwirty.ma/products/{produit.get('handle')}?variant={variant.get('id')}"
                })

        return jsonify({"error": "Variante non trouvée pour ce libellé."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500



