from flask import Flask, send_file, request, jsonify
import re

app = Flask(__name__)

# In-memory storage (fast, reliable)
downtime_events = []  # list of {"machine": "CNC Machine", "cause": "power failure"}

# Mapping from spoken names to display names
NAME_MAP = {
    "cnc": "CNC Machine",
    "cnc machine": "CNC Machine",
    "lathe": "Lathe Machine",
    "lathe machine": "Lathe Machine",
    "grinder": "Grinder",
    "grinder machine": "Grinder",
    "machine 1": "CNC Machine",
    "machine 2": "Lathe Machine",
    "machine 3": "Grinder",
    "1": "CNC Machine",
    "2": "Lathe Machine",
    "3": "Grinder",
}

def extract_downtime_info(text):
    text_lower = text.lower()
    result = {"machine": None, "cause": "unknown"}
    
    # Find machine name (priority: named machines over numbers)
    for key, display_name in NAME_MAP.items():
        if key in text_lower:
            result["machine"] = display_name
            break
    
    # Find cause (simple keyword matching)
    if "bearing" in text_lower:
        result["cause"] = "bearing failure"
    elif "motor" in text_lower:
        result["cause"] = "motor failure"
    elif "power" in text_lower or "bijli" in text_lower or "electric" in text_lower:
        result["cause"] = "power failure"
    elif "belt" in text_lower:
        result["cause"] = "belt broken"
    elif "operator" in text_lower or "chai" in text_lower or "absent" in text_lower:
        result["cause"] = "operator absent"
    
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
    
    if extracted["machine"]:
        # Add to in-memory list (avoid duplicates for same machine? keep as is)
        downtime_events.append({"machine": extracted["machine"], "cause": extracted["cause"]})
        return f"✅ {extracted['machine']} downtime logged. Cause: {extracted['cause']}"
    else:
        return "❌ Please say machine name or number, e.g., 'CNC machine stopped, power failure'"

@app.route('/get_events')
def get_events():
    return jsonify({"events": downtime_events})

@app.route('/reset')
def reset():
    downtime_events.clear()
    return jsonify({"status": "reset"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)