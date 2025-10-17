from flask import Flask, request, jsonify, send_from_directory
import csv
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import os

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

# --- Tải sẵn model dịch (nhẹ, phù hợp Render Free) ---
print("🔄 Đang tải model VietAI/envit5-translation...")
model_name = "VietAI/envit5-translation"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cpu")
print("✅ Model đã sẵn sàng!")

# --- Hàm dịch ---
def translate_en_to_vi(text):
    if not text.strip():
        return ""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=256)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

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
        # 2 từ trở lên → dùng model dịch
        translation = translate_en_to_vi(text)
        result = translation

    return jsonify({"result": result})

# --- Cấu hình cho Render ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Server chạy tại port {port}")
    app.run(host="0.0.0.0", port=port)
