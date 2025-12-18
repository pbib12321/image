import os
import requests
import io
import zipfile
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

API_KEY = "AIzaSyBajJF8VF8wsl9fZd8IXjQs_g3Sz3CZ0_Q"  # Your API Key
CX = "f2d5b992986d4480f"  # Your CSE ID

def fetch_image_urls(query, num_images):
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
            break

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

    return images

@app.route("/images", methods=["POST"])
def get_images():
    data = request.json
    query = data.get("query", "").strip()
    num_images = int(data.get("num_images", 5))

    if not query:
        return jsonify({"error": "Query is required"}), 400

    images = fetch_image_urls(query, num_images)
    return jsonify({"query": query, "num_images": len(images), "images": images})

@app.route("/download_zip", methods=["POST"])
def download_zip():
    data = request.json
    query = data.get("query", "").strip()
    num_images = int(data.get("num_images", 5))

    if not query:
        return jsonify({"error": "Query is required"}), 400

    images = fetch_image_urls(query, num_images)

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for idx, url in enumerate(images, start=1):
            try:
                img_data = requests.get(url, timeout=10).content
                ext = os.path.splitext(urlparse(url).path)[1]
                if not ext or len(ext) > 5:
                    ext = ".jpg"
                zipf.writestr(f"{query}_{idx}{ext}", img_data)
            except:
                continue

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{query}.zip"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

