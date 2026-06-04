from flask import Flask, jsonify, request
from datetime import datetime
import re

app = Flask(__name__)

# ==================== CONFIG ====================
OWNER = "@notxsatvir"
CHANNEL = "https://t.me/notxsatvir"
VERSION = "2.0.0"

# ==================== VALIDATION ====================
def is_valid_gst(gst):
    if not gst or len(gst) != 15:
        return False
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst.upper()))

# ==================== DEMO DATABASE ====================
DEMO_DATA = {
    "07AAACA1234A1Z": {
        "business_name": "ABC CORPORATION PRIVATE LIMITED",
        "trade_name": "ABC CORP",
        "status": "Active",
        "registration_date": "2015-04-12",
        "state": "Delhi",
        "state_code": "07",
        "pan": "AAACA1234A",
        "gst_type": "Regular",
        "return_period": "Monthly",
        "last_return_filed": "2026-03-20"
    },
    "24AAAAA1234A1Z": {
        "business_name": "GUJARAT TRADING COMPANY",
        "trade_name": "GUJ TRADING",
        "status": "Active",
        "registration_date": "2018-07-22",
        "state": "Gujarat",
        "state_code": "24",
        "pan": "AAAAA1234A",
        "gst_type": "Regular",
        "return_period": "Quarterly"
    },
    "27AAAAA1234A1Z": {
        "business_name": "MAHARASHTRA ENTERPRISES",
        "trade_name": "MH ENTERPRISES",
        "status": "Active",
        "registration_date": "2019-01-15",
        "state": "Maharashtra",
        "state_code": "27",
        "pan": "AAAAA1234A",
        "gst_type": "Composition",
        "return_period": "Quarterly"
    }
}

# ==================== MAIN ROUTES ====================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "success": True,
        "owner": OWNER,
        "channel": CHANNEL,
        "version": VERSION,
        "message": "GST API is running successfully",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "GET /": "Home page - API info",
            "GET /health": "Health check",
            "GET /api/gst?gst=NUMBER": "Get GST details",
            "GET /api/gst/NUMBER": "Get GST details by path",
            "POST /api/gst": "Post JSON with GST number"
        },
        "example": "/api/gst?gst=07AAACA1234A1Z",
        "demo_gst_numbers": ["07AAACA1234A1Z", "24AAAAA1234A1Z", "27AAAAA1234A1Z"]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "owner": OWNER,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat(),
        "uptime": "API is live"
    })

@app.route('/api/gst', methods=['GET'])
def gst_lookup():
    gst = request.args.get('gst') or request.args.get('gstin') or request.args.get('query')
    
    if not gst:
        return jsonify({
            "success": False,
            "owner": OWNER,
            "error": "GST number is required",
            "usage": "/api/gst?gst=07AAACA1234A1Z",
            "example_gst": "07AAACA1234A1Z"
        }), 400
    
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return jsonify({
            "success": False,
            "owner": OWNER,
            "error": "Invalid GST number format",
            "message": "GST number must be 15 characters",
            "format_example": "07AAACA1234A1Z",
            "provided_gst": gst
        }), 400
    
    # Check in demo database
    if gst in DEMO_DATA:
        data = DEMO_DATA[gst].copy()
        data["gstin"] = gst
        data["is_demo"] = True
        return jsonify({
            "success": True,
            "owner": OWNER,
            "channel": CHANNEL,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    # Generate dynamic data for any valid GST number
    return jsonify({
        "success": True,
        "owner": OWNER,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "gstin": gst,
            "business_name": f"BUSINESS_{gst[2:7]}",
            "trade_name": f"TRADE_{gst[2:5]}",
            "status": "Active",
            "registration_date": "2020-01-01",
            "state": "Unknown",
            "state_code": gst[:2],
            "pan": gst[2:12] if len(gst) >= 12 else "AAAAA0000A",
            "gst_type": "Regular",
            "is_demo": True,
            "note": "This is demo data. Real GST API integration coming soon."
        }
    })

@app.route('/api/gst/<gst>', methods=['GET'])
def gst_lookup_path(gst):
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return jsonify({
            "success": False,
            "owner": OWNER,
            "error": "Invalid GST number format",
            "message": "GST number must be 15 characters",
            "provided_gst": gst
        }), 400
    
    if gst in DEMO_DATA:
        data = DEMO_DATA[gst].copy()
        data["gstin"] = gst
        return jsonify({
            "success": True,
            "owner": OWNER,
            "channel": CHANNEL,
            "timestamp": datetime.now().isoformat(),
            "data": data
        })
    
    return jsonify({
        "success": True,
        "owner": OWNER,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat(),
        "data": {
            "gstin": gst,
            "business_name": f"BUSINESS_{gst[2:7]}",
            "trade_name": f"TRADE_{gst[2:5]}",
            "status": "Active",
            "state_code": gst[:2],
            "pan": gst[2:12] if len(gst) >= 12 else "AAAAA0000A",
            "is_demo": True
        }
    })

@app.route('/api/gst', methods=['POST'])
def gst_lookup_post():
    try:
        data = request.get_json(force=True, silent=True) or {}
        gst = data.get('gst') or data.get('gstin') or data.get('query')
        
        if not gst:
            return jsonify({
                "success": False,
                "owner": OWNER,
                "error": "GST number required in JSON body",
                "example": {"gst": "07AAACA1234A1Z"}
            }), 400
        
        gst = gst.strip().upper()
        
        if not is_valid_gst(gst):
            return jsonify({
                "success": False,
                "owner": OWNER,
                "error": "Invalid GST number format",
                "provided_gst": gst
            }), 400
        
        if gst in DEMO_DATA:
            return jsonify({
                "success": True,
                "owner": OWNER,
                "channel": CHANNEL,
                "timestamp": datetime.now().isoformat(),
                "data": DEMO_DATA[gst]
            })
        
        return jsonify({
            "success": True,
            "owner": OWNER,
            "channel": CHANNEL,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "gstin": gst,
                "business_name": f"BUSINESS_{gst[2:7]}",
                "status": "Active",
                "state_code": gst[:2]
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "owner": OWNER,
            "error": f"Invalid JSON: {str(e)}"
        }), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "success": False,
        "owner": OWNER,
        "error": "Endpoint not found",
        "available_endpoints": [
            "/",
            "/health",
            "/api/gst?gst=GST_NUMBER",
            "/api/gst/GST_NUMBER"
        ]
    }), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)