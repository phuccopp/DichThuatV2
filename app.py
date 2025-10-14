from flask import Flask, request, jsonify, send_from_directory
import csv

# Khởi tạo Flask, chỉ định folder chứa static HTML
app = Flask(__name__, static_folder='static')

# --- Load từ điển CSV ---
dictionary = {}
with open("dictionary.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Chuẩn hóa key: lowercase + strip khoảng trắng đầu/cuối
        key = row['english'].strip().lower()
        dictionary[key] = {
            'phonetic': row['phonetic'].strip(),
            'vietnamese': row['vietnamese'].strip()
        }

# --- Route trả file index.html ---
@app.route("/", methods=["GET"])
def home():
    return send_from_directory(app.static_folder, 'index.html')

# --- API dịch văn bản ---
@app.route("/translate", methods=["POST"])
def translate():
    data = request.json
    text = data.get("text", "").lower().strip()
    words = text.split()
    translated_words = []
    i = 0
    max_phrase_len = 3  # thử tối đa 3 từ cùng lúc, bạn có thể tăng nếu cần

    while i < len(words):
        # Thử n-gram dài xuống ngắn
        for n in range(max_phrase_len, 0, -1):
            phrase = " ".join(words[i:i+n]).strip()
            if phrase in dictionary:
                item = dictionary[phrase]
                translated_words.append(f"{phrase} [{item['phonetic']}] → {item['vietnamese']}")
                i += n
                break
        else:
            # Nếu không tìm thấy trong dictionary, giữ nguyên từ
            translated_words.append(words[i])
            i += 1

    result = " | ".join(translated_words)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
