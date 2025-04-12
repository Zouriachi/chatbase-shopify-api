import os
import requests
from flask import Blueprint, jsonify

products_bp = Blueprint("products", __name__)

SHOPIFY_STORE_NAME = os.getenv("SHOPIFY_STORE_NAME")
SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ADMIN_TOKEN
}

@products_bp.route("/products", methods=["GET"])
def get_all_products():
    
    print("SHOPIFY_STORE_NAME =", SHOPIFY_STORE_NAME)
    print("SHOPIFY_ADMIN_TOKEN =", SHOPIFY_ADMIN_TOKEN)

    url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json"
    response = requests.get(url, headers=HEADERS)
    
    print("Status code:", response.status_code)
    print("Response text:", response.text)


    
    if response.status_code != 200:
        return jsonify({"error": "Erreur lors de la récupération des produits."}), 500

    return jsonify(response.json())
