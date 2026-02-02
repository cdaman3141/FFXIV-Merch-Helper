from flask import Flask, jsonify, send_file
import json
import os
import subprocess
import sys

app = Flask(__name__, static_folder=os.path.dirname(__file__))
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_PATH = os.path.join(WORKSPACE_DIR, "lamia_price_check.py")
JSON_OUTPUT = os.path.join(WORKSPACE_DIR, "lamia_data.json")


@app.route("/")
def index():
    return send_file(os.path.join(WORKSPACE_DIR, "ui.html"))


@app.route("/api/fetch-prices", methods=["GET"])
def fetch_prices():
    """Run the price check script and return the JSON data"""
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, SCRIPT_PATH],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            return (
                jsonify(
                    {
                        "error": f"Script failed: {result.stderr}",
                        "stdout": result.stdout,
                    }
                ),
                500,
            )

        # Load and return the JSON data
        if not os.path.exists(JSON_OUTPUT):
            return jsonify({"error": "Script did not generate output file"}), 500

        with open(JSON_OUTPUT, "r", encoding="utf-8") as f:
            data = json.load(f)

        return jsonify({"success": True, "data": data, "message": result.stdout})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script took too long to run"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(f"Starting server at http://localhost:5000")
    print(f"Open your browser to http://localhost:5000")
    app.run(debug=True, host="127.0.0.1", port=5000)
