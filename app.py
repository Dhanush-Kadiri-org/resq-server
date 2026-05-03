# from flask import Flask, request, jsonify
# import numpy as np
# import tensorflow_hub as hub
# import soundfile as sf
# import requests
# import csv, io

# app = Flask(__name__)

# # ---------------- CONFIG ----------------
# TOKEN = "8720620862:AAH5JYHtfZhNxG91n60VFASGkwBGipRj08o"
# CHAT_ID = "5172692730"

# # ---------------- LOAD MODEL ----------------
# print("Loading YAMNet...")
# model = hub.load("https://tfhub.dev/google/yamnet/1")
# print("✅ Model Loaded")

# # ---------------- LOAD LABELS ----------------
# def load_labels():
#     url = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
#     response = requests.get(url)
#     reader = csv.reader(io.StringIO(response.text))
#     next(reader)
#     return [row[2] for row in reader]

# labels = load_labels()

# # ---------------- TELEGRAM ----------------
# def send_message(msg):
#     url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
#     requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# def send_audio(file_path):
#     url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
#     with open(file_path, 'rb') as f:
#         requests.post(url, data={"chat_id": CHAT_ID}, files={"document": f})

# # ---------------- CLASSIFY ----------------
# def classify(audio):
#     scores, _, _ = model(audio)
#     scores = scores.numpy()
#     mean_scores = np.mean(scores, axis=0)

#     top_idx = np.argsort(mean_scores)[-5:][::-1]
#     return [(labels[i], mean_scores[i]) for i in top_idx]

# # ---------------- DETECTION ----------------
# def detect_emergency(results):
#     for label, conf in results:
#         l = label.lower()

#         if conf > 0.3:
#             if any(x in l for x in ["scream", "cry", "gunshot"]):
#                 return "CONFIRMED"
#             if any(x in l for x in ["cough", "breathing", "wheeze"]):
#                 return "MEDICAL"

#     return "UNCERTAIN"

# # ---------------- API ----------------
# @app.route("/upload", methods=["POST"])
# def upload():

#     file = request.files["audio"]
#     hr = request.form.get("heart_rate")

#     filename = "received.wav"
#     file.save(filename)

#     # Read audio
#     audio, sr = sf.read(filename)
#     audio = audio.astype(np.float32)

#     # Normalize
#     audio = audio / (np.max(np.abs(audio)) + 1e-6)

#     # Classify
#     results = classify(audio)

#     print("\n🔍 Predictions:")
#     for label, conf in results:
#         print(f"{label} → {round(conf,2)}")

#     status = detect_emergency(results)

#     # Send alert
#     msg = f"🚨 {status}\nHeart Rate: {hr}"

#     send_message(msg)
#     send_audio(filename)

#     return jsonify({
#         "status": status,
#         "heart_rate": hr
#     })

# # ---------------- RUN ----------------
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)









from flask import Flask, request, jsonify
import numpy as np
import tensorflow_hub as hub
import soundfile as sf
import requests
import csv, io

app = Flask(__name__)

# ---------------- CONFIG ----------------
TOKEN = "8720620862:AAH5JYHtfZhNxG91n60VFASGkwBGipRj08o"
CHAT_ID = "5172692730"

# ---------------- LOAD MODEL ----------------
print("Loading YAMNet...")
model = hub.load("https://tfhub.dev/google/yamnet/1")
print("✅ Model Loaded")

# ---------------- LOAD LABELS ----------------
def load_labels():
    url = "https://raw.githubusercontent.com/tensorflow/models/master/research/audioset/yamnet/yamnet_class_map.csv"
    response = requests.get(url)
    reader = csv.reader(io.StringIO(response.text))
    next(reader)
    return [row[2] for row in reader]

labels = load_labels()

# ---------------- TELEGRAM ----------------
def send_message(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def send_audio(file_path):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, 'rb') as f:
        requests.post(url, data={"chat_id": CHAT_ID}, files={"document": f})

# ---------------- CLASSIFY ----------------
def classify(audio):
    scores, _, _ = model(audio)
    scores = scores.numpy()
    mean_scores = np.mean(scores, axis=0)

    top_idx = np.argsort(mean_scores)[-5:][::-1]
    return [(labels[i], mean_scores[i]) for i in top_idx]

# ---------------- DETECTION ----------------
def detect_emergency(results):
    for label, conf in results:
        l = label.lower()

        if conf > 0.3:
            if any(x in l for x in ["scream", "cry", "gunshot", "explosion"]):
                return "THREAT"

            if any(x in l for x in ["cough", "breathing", "wheeze", "snore"]):
                return "MEDICAL"

    return "UNDETECTED"

# ---------------- API ----------------
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["audio"]
    hr = request.form.get("heart_rate")
    location = request.form.get("location")

    filename = "received.wav"
    file.save(filename)

    # Load audio
    audio, sr = sf.read(filename)
    audio = audio.astype(np.float32)
    audio = audio / (np.max(np.abs(audio)) + 1e-6)

    # Classify
    results = classify(audio)

    print("\n🔍 Predictions:")
    for label, conf in results:
        print(f"{label} → {round(conf,2)}")

    status = detect_emergency(results)
    top_label = results[0][0]

    # ---------------- MESSAGE ----------------
    if status == "THREAT":
        msg = "🚨 THREAT EMERGENCY"

    elif status == "MEDICAL":
        msg = "🏥 MEDICAL EMERGENCY"

    else:
        msg = "⚠️ UNDETECTED EMERGENCY (HR abnormal)"

    msg += f"\nHeart Rate: {hr}"
    msg += f"\nDetected Sound: {top_label}"

    if location:
        msg += f"\nLocation: {location}"
    else:
        msg += "\nLocation: Not available"

    # Send
    send_message(msg)
    send_audio(filename)

    return jsonify({
        "status": status,
        "heart_rate": hr,
        "sound": top_label
    })

# ---------------- RUN ----------------
import os

port = int(os.environ.get("PORT", 5000))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port)