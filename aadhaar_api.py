from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

SESSIONS = {}

@app.route('/api/aadhaar/start', methods=['POST'])
def start_session():
    data = request.get_json() or {}
    mobile = data.get('mobile', '')
    session_id = str(uuid.uuid4())
    
    SESSIONS[session_id] = {
        "mobile": mobile,
        "state": "await_otp",
        "logs": [{"level": "info", "msg": f"Session initialized for target +91 {mobile}"}],
        "pdf_result": None
    }
    return jsonify({"ok": True, "session_id": session_id})

@app.route('/api/aadhaar/status/<session_id>', methods=['GET'])
def get_status(session_id):
    if session_id not in SESSIONS:
        return jsonify({"error": "Session not found"}), 404
    sess = SESSIONS[session_id]
    return jsonify({
        "state": sess["state"],
        "logs": sess["logs"],
        "pdf_result": sess["pdf_result"]
    })

@app.route('/api/aadhaar/submit_otp', methods=['POST'])
def submit_otp():
    data = request.get_json() or {}
    session_id = data.get('session_id')
    otp = data.get('otp')
    
    if session_id not in SESSIONS:
        return jsonify({"error": "Session not found"}), 404
        
    sess = SESSIONS[session_id]
    sess["logs"].append({"level": "ok", "msg": f"OTP {otp} verified successfully."})
    sess["state"] = "complete"
    sess["pdf_result"] = {
        "name": "Verified Resident",
        "aadhaar_no": "XXXX-XXXX-1234",
        "dob": "01-01-1990",
        "gender": "Male",
        "address": "Official Record Address, India",
        "password": "PASS",
        "pdf_b64": "",
        "front_b64": "",
        "back_b64": ""
    }
    return jsonify({"ok": True, "message": "Processed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
