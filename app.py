from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

app = Flask(__name__)

# Initialize Firebase safely
if not firebase_admin._apps:
    firebase_admin.initialize_app()

db = firestore.client()

@app.route("/register", methods=["POST"])
def register_doctor():

    data = request.get_json()

    doctor_name = data.get("DoctorName")
    slmc_id = data.get("SLMC_ID")

    if not doctor_name or not slmc_id:
        return jsonify({"message": "DoctorName and SLMC_ID required"}), 400

    doc_ref = db.collection("Doctors").document(slmc_id)
    doc = doc_ref.get()

    if doc.exists:

        doctor_data = doc.to_dict()

        if doctor_data["Completed"]:
            return jsonify({"message": "Doctor is already registered"}), 400
        else:
            return jsonify({"message": "Doctor already exists but game not completed"}), 200

    doc_ref.set({
        "DoctorName": doctor_name,
        "SLMC_ID": slmc_id,
        "LoginTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Score": 0,
        "Completed": False
    })

    return jsonify({"message": "Doctor registered successfully"}), 201


@app.route("/update-score", methods=["POST"])
def update_score():

    data = request.get_json()

    slmc_id = data.get("SLMC_ID")
    score = data.get("Score")
    completed = data.get("Completed")

    doc_ref = db.collection("Doctors").document(slmc_id)
    doc = doc_ref.get()

    if not doc.exists:
        return jsonify({"message": "Doctor not found"}), 404

    update_data = {"Score": score}

    if completed:
        update_data["Completed"] = True

    doc_ref.update(update_data)

    return jsonify({"message": "Score updated successfully"})


@app.route("/")
def home():
    return "Doctor Game API Running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)