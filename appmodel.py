from flask import Flask, request, jsonify, send_from_directory
import csv
from transformers import MarianMTModel, MarianTokenizer
import os

# --- Khởi tạo Flask ---
app = Flask(__name__, static_folder='static')

# --- Lấy token từ biến môi trường ---
HF_TOKEN = os.environ.get("HF_TOKEN")

# --- Load dictionary CSV ---
dictionary = {}
with open("dictionary.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        key = row['english'].strip().lower()
        dictionary[key] = {
            'phonetic': row['phonetic'].strip(),
            'vietnamese': row['vietnamese'].strip()
        }

# --- Load model ---
model_name = "Helsinki-NLP/opus-mt-en-vi"
tokenizer = MarianTokenizer.from_pretrained(model_name, token=HF_TOKEN)
model = MarianMTModel.from_pretrained(model_name, token=HF_TOKEN).to("cpu")

def translate_en_to_vi(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
    outputs = model.generate(**inputs, max_length=128, num_beams=5, no_repeat_ngram_size=2)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# --- Route trả file HTML ---
@app.route("/", methods=["GET"])
def home():
    return send_from_directory(app.static_folder, 'index.html')

# --- API chính ---
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "").strip().lower()

    if not text:
        return jsonify({"result": ""})

    words = text.split()

    if len(words) == 1:
        if text in dictionary:
            item = dictionary[text]
            result = f"{text} [{item['phonetic']}] → {item['vietnamese']}"
        else:
            result = "Không tìm thấy trong từ điển."
    else:
        translation = translate_en_to_vi(text)
        result = f"{translation}"

    return jsonify({"result": result})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
