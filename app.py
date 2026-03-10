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
    
@app.route("/doctors", methods=["GET"])
def get_all_doctors():

    doctors_ref = db.collection("Doctors").stream()

    doctors = []

    for doc in doctors_ref:
        doctor_data = doc.to_dict()
        doctors.append(doctor_data)

    return jsonify({
        "count": len(doctors),
        "doctors": doctors
    })

@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        # Reference to the Doctors collection
        doctors_ref = db.collection("Doctors")

        # Query top 10 doctors sorted by Score descending
        top_doctors = doctors_ref.order_by("Score", direction=firestore.Query.DESCENDING).limit(10).stream()

        leaderboard = []
        for doc in top_doctors:
            data = doc.to_dict()
            leaderboard.append({
                "DoctorName": data.get("DoctorName"),
                "SLMC_ID": data.get("SLMC_ID"),
                "Score": data.get("Score"),
                "Completed": data.get("Completed")
            })

        return jsonify({"leaderboard": leaderboard}), 200

    except Exception as e:
        return jsonify({"message": "Error fetching leaderboard", "error": str(e)}), 500

@app.route("/")
def home():
    return "Doctor Game API Running"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)