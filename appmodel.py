from flask import Flask, request, jsonify, send_from_directory
import csv
from transformers import MarianMTModel, MarianTokenizer

# --- Khởi tạo Flask ---
app = Flask(__name__, static_folder='static')

# --- Load dictionary CSV ---
dictionary = {}
with open("dictionary.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = row["english"].strip().lower()
        dictionary[key] = {
            "phonetic": row["phonetic"].strip(),
            "vietnamese": row["vietnamese"].strip(),
        }

# --- Load model dịch Anh-Việt ---
model_name = "Helsinki-NLP/opus-mt-en-vi"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name).to("cpu")

def translate_en_to_vi(text):
    """Dịch bằng model Anh → Việt"""
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
    outputs = model.generate(
        **inputs, max_length=128, num_beams=5, no_repeat_ngram_size=2
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# --- Route trang chủ ---
@app.route("/", methods=["GET"])
def home():
    return send_from_directory(app.static_folder, "index.html")

# --- API dịch ---
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "").strip().lower()

    if not text:
        return jsonify({"result": ""})

    words = text.split()

    # Nếu chỉ 1 từ -> tra dictionary
    if len(words) == 1:
        if text in dictionary:
            item = dictionary[text]
            result = f"{text} [{item['phonetic']}] → {item['vietnamese']}"
        else:
            result = "Không tìm thấy trong từ điển."
    else:
        # Nếu từ 2 từ trở lên -> dùng model
        translation = translate_en_to_vi(text)
        result = translation

    return jsonify({"result": result})

# --- Chạy app (Render sẽ tự cấp PORT) ---
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
