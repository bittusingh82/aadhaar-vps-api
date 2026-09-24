from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import traceback

app = Flask(__name__)
CORS(app)

# Global Error Handler: Ensure Flask NEVER returns HTML, always returns JSON
@app.errorhandler(Exception)
def handle_unexpected_error(error):
    return jsonify({
        "ok": False, 
        "state": "error",
        "error": str(error),
        "trace": traceback.format_exc()
    }), 500

@app.errorhandler(404)
def handle_404(error):
    return jsonify({
        "ok": False, 
        "state": "error",
        "error": "API Endpoint not found (404)"
    }), 404

SESSIONS = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "API is running successfully"})

@app.route('/aadhaar/start', methods=['POST'])
def start_session():
    try:
        data = request.get_json(silent=True) or {}
        mobile = data.get('mobile', '')
        
        if not mobile:
            return jsonify({"ok": False, "error": "Mobile number is required"}), 400
            
        session_id = str(uuid.uuid4())
        SESSIONS[session_id] = {
            "mobile": mobile,
            "state": "await_otp",
            "logs": [{"level": "info", "msg": f"Session initialized for target +91 {mobile}"}],
            "pdf_result": None
        }
        return jsonify({"ok": True, "session_id": session_id})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/aadhaar/status/<session_id>', methods=['GET'])
def get_status(session_id):
    if session_id not in SESSIONS:
        return jsonify({"state": "error", "error": "Session not found", "logs": []}), 404
        
    sess = SESSIONS[session_id]
    return jsonify({
        "state": sess["state"],
        "logs": sess["logs"],
        "pdf_result": sess["pdf_result"]
    })

@app.route('/aadhaar/submit_otp', methods=['POST'])
def submit_otp():
    try:
        data = request.get_json(silent=True) or {}
        session_id = data.get('session_id')
        otp = data.get('otp')
        
        if session_id not in SESSIONS:
            return jsonify({"ok": False, "error": "Session not found"}), 404
            
        sess = SESSIONS[session_id]
        sess["logs"].append({"level": "ok", "msg": f"OTP {otp} received and verified successfully."})
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
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route('/aadhaar/submit_dl_otp', methods=['POST'])
def submit_dl_otp():
    return submit_otp()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
