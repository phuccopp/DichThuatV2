from flask import Flask, request, jsonify, send_from_directory
import csv
import os
import requests

# --- Khởi tạo Flask ---
app = Flask(__name__, static_folder='static')

# --- Load dictionary CSV ---
dictionary = {}
try:
    with open("dictionary.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row['english'].strip().lower()
            dictionary[key] = {
                'phonetic': row['phonetic'].strip(),
                'vietnamese': row['vietnamese'].strip()
            }
    print("✅ Dictionary loaded!")
except Exception as e:
    print(f"⚠️ Không thể tải dictionary.csv: {e}")

# --- Hugging Face API setup ---
HF_TOKEN = os.environ.get("HF_TOKEN")  # set token trên Render
HF_API_URL = "https://api-inference.huggingface.co/models/VietAI/envit5-translation"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def translate_en_to_vi(text):
    """Dùng API Hugging Face dịch từ tiếng Anh sang tiếng Việt"""
    if not text.strip():
        return ""
    payload = {"inputs": text}
    try:
        response = requests.post(HF_API_URL, headers=HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and "generated_text" in result[0]:
                return result[0]["generated_text"]
        return "⚠️ Lỗi khi gọi API Hugging Face."
    except Exception as e:
        return f"⚠️ Exception khi gọi API: {e}"

# --- Route trả file HTML ---
@app.route("/", methods=["GET"])
def home():
    return send_from_directory(app.static_folder, "index.html")

# --- API chính ---
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "").strip().lower()

    if not text:
        return jsonify({"result": ""})

    words = text.split()

    # 1 từ → tra từ điển
    if len(words) == 1:
        if text in dictionary:
            item = dictionary[text]
            result = f"{text} [{item['phonetic']}] → {item['vietnamese']}"
        else:
            result = "Không tìm thấy trong từ điển."
    else:
        # 2 từ trở lên → gọi API Hugging Face
        result = translate_en_to_vi(text)

    return jsonify({"result": result})

# --- Cấu hình cho Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server chạy tại port {port}")
    app.run(host="0.0.0.0", port=port)
