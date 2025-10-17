from flask import Flask, request, jsonify
import csv
from googletrans import Translator

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

# --- Khởi tạo Google Translator ---
translator = Translator()

# --- Route trả file HTML ---
@app.route("/", methods=["GET"])
def home():
    return "Server is running"  # Bạn có thể trả index.html nếu có static folder

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
        # 2 từ trở lên → dùng Google Translate
        try:
            translation = translator.translate(text, src='en', dest='vi')
            result = translation.text
        except Exception as e:
            result = f"⚠️ Lỗi Google Translate: {e}"

    return jsonify({"result": result})

# --- Chạy Flask ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server chạy tại port {port}")
    app.run(host="0.0.0.0", port=port)
