import os
import requests
from flask import Blueprint, request, jsonify

product_info_bp = Blueprint("product_info", __name__)

SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")
SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN
}


def clean(text):
    return text.lower().replace(" ", "").replace("cm", "").strip()


@product_info_bp.route("/product-info", methods=["GET"])
def get_product_info():
    title = request.args.get("title")
    size = request.args.get("size")

    if not title or not size:
        return jsonify({"error": "Title et size requis"}), 400

    try:
        url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json?title={title}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()

        if not data.get("products"):
            return jsonify({"error": "Produit non trouvé."}), 404

        produit = data["products"][0]  # Premier match

        cleaned_requested_size = clean(size)

        for variant in produit.get("variants", []):
            if cleaned_requested_size in clean(variant.get("title", "")):
                return jsonify({
                    "produit": produit.get("title"),
                    "taille demandée": size,
                    "variante trouvée": variant.get("title"),
                    "prix": variant.get("price") + " MAD",
                    "disponible": variant.get("inventory_quantity", 0) > 0
                })

        return jsonify({
            "produit": produit.get("title"),
            "taille demandée": size,
            "message": "Aucune variante trouvée correspondant à la taille indiquée."
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
