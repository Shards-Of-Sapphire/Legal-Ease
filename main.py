from app import app
from flask import Flask
from flask_cors import CORS
from flask import Flask, request, jsonify
import traceback

CORS(app)
app = Flask(__name__)

if __name__ == "__main__":
    app.run()


@app.route("/upload", methods=["POST"])
def upload():
    try:
        file = request.files.get("file")
        captured_image = request.form.get("captured_image")

        if not file and not captured_image:
            return jsonify({"error": "No file provided"}), 400

        # ---- YOUR EXISTING LOGIC HERE ----
        # extract text
        # generate summary
        # detect key clauses

        summary = "Your generated summary here"
        key_clauses = [
            {
                "type": "Confidentiality",
                "content": "Clause text here",
                "explanation": "This clause means..."
            }
        ]

        return jsonify({
            "success": True,
            "summary": summary,
            "key_clauses": key_clauses
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500
