from flask import Flask, render_template, request, jsonify, send_file
import requests
import random
import io
from PIL import Image
from flask_cors import CORS   # ✅ NEW

app = Flask(__name__)
CORS(app)  # ✅ allows frontend requests

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}"

STYLES = {
    "none": "",
    "photorealistic": "photorealistic, ultra detailed, 8k",
    "oil_painting": "oil painting, fine art",
    "anime": "anime style, vibrant colors",
}

SIZES = {
    "512x512": (512, 512),
    "768x512": (768, 512),
    "1024x1024": (1024, 1024),
}


@app.route("/")
def index():
    return render_template("index.html", styles=STYLES, sizes=list(SIZES.keys()))


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()

        prompt = data.get("prompt", "").strip()
        style = data.get("style", "none")
        size = data.get("size", "512x512")
        count = min(int(data.get("count", 2)), 4)

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        style_suffix = STYLES.get(style, "")
        full_prompt = f"{prompt}, {style_suffix}" if style_suffix else prompt

        w, h = SIZES.get(size, (512, 512))

        results = []
        for _ in range(count):
            seed = random.randint(1, 9999999)

            url = (
                POLLINATIONS_URL.format(prompt=requests.utils.quote(full_prompt))
                + f"?width={w}&height={h}&seed={seed}&nologo=true"
            )

            print("Generated URL:", url)  # ✅ DEBUG

            results.append({"url": url, "seed": seed})

        return jsonify({"images": results})

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Server error"}), 500


@app.route("/download")
def download():
    url = request.args.get("url")

    try:
        resp = requests.get(url)
        img = Image.open(io.BytesIO(resp.content))

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return send_file(buf, mimetype="image/png", as_attachment=True, download_name="image.png")

    except Exception as e:
        return f"Download failed: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)