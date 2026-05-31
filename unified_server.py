from flask import Flask, send_file, request, jsonify
import re
import os

app = Flask(__name__)

LOG_FILE = "downtime_log.txt"

def extract_downtime_info(text):
    result = {"machine_number": None, "cause": "unknown"}
    
    match = re.search(r'machine\s*(\d+)|मशीन\s*(\d+)', text, re.IGNORECASE)
    if match:
        result["machine_number"] = int(match.group(1) or match.group(2))
    
    if "bearing" in text.lower():
        result["cause"] = "bearing failure"
    elif "motor" in text.lower():
        result["cause"] = "motor failure"
    elif "power" in text.lower() or "bijli" in text.lower():
        result["cause"] = "power failure"
    
    return result

@app.route('/')
def dashboard():
    return send_file('dashboard.html')

@app.route('/worker')
def worker():
    return send_file('voice_recorder.html')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").lower()
    extracted = extract_downtime_info(incoming_msg)
    
    if extracted["machine_number"]:
        with open(LOG_FILE, "a") as f:
            f.write(f"{extracted['machine_number']}|{extracted['cause']}\n")
        return f"✅ Machine {extracted['machine_number']} downtime logged. Cause: {extracted['cause']}"
    else:
        return "❌ Please say: Machine X stopped, cause"

@app.route('/get_events')
def get_events():
    events = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    events.append({"machine": parts[0], "cause": parts[1]})
    return jsonify({"events": events})

@app.route('/reset')
def reset():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return jsonify({"status": "reset"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)