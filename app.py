import os
import io
import requests
from flask import Flask, request, jsonify, send_file
from urllib.parse import urlparse

app = Flask(__name__)

API_KEY = "AIzaSyBajJF8VF8wsl9fZd8IXjQs_g3Sz3CZ0_Q"  # Your API key
CX = "f2d5b992986d4480f"  # Your CSE ID

@app.route("/images", methods=["POST"])
def get_images():
    data = request.json
    query = data.get("query", "").strip()
    num_images = int(data.get("num_images", 5))

    if not query:
        return jsonify({"error": "Query is required"}), 400

    images = []
    start_index = 1
    downloaded = 0

    while downloaded < num_images:
        url = (
            f"https://www.googleapis.com/customsearch/v1"
            f"?key={API_KEY}&cx={CX}&q={query}"
            f"&searchType=image&start={start_index}&num={min(10, num_images - downloaded)}"
        )

        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({"error": f"Google API error: {response.status_code}", "details": response.text}), 500

        data = response.json()
        items = data.get("items", [])

        if not items:
            break

        for item in items:
            img_url = item.get("link")
            if img_url:
                images.append(img_url)
                downloaded += 1
            if downloaded >= num_images:
                break

        start_index += len(items)

    return jsonify({"query": query, "num_images": len(images), "images": images})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
