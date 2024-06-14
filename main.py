import firebase_admin
from firebase_admin import credentials, firestore, auth
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialise Firebase
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred)
db = firestore.client()

# --- Authentication Helper (Backend) ---
def is_authenticated(request):
    """Verifies Firebase ID token from the frontend."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False, jsonify({"error": "Unauthorized"}), 401
    token = auth_header.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(token)
        return True, decoded_token, 200
    except Exception as e:
        return False, jsonify({"error": "Invalid token"}), 401

# --- User Management ---

@app.route('/api/users', methods=['POST'])
def create_user():
    is_valid, data, status_code = is_authenticated(request)
    if not is_valid:
        return data, status_code

    user_id = data['uid']
    try:
        user_data = request.get_json()
        db.collection('users').document(user_id).set(user_data, merge=True)
        return jsonify({"message": "User data updated", "uid": user_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Pet Management ---

@app.route('/api/pets', methods=['POST'])
def create_pet():
    is_valid, data, status_code = is_authenticated(request)
    if not is_valid:
        return data, status_code

    user_id = data['uid']  
    try:
        pet_data = request.get_json()
        pet_data['ownerId'] = user_id # Automatically associate with the logged-in user

        db.collection('pets').add(pet_data)
        return jsonify({"message": "Pet created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Dog Walker Management (Similar structure to User/Pet) ---
# ... 

# --- Search Functionality (Example) ---
@app.route('/api/walkers', methods=['GET'])
def search_walkers():
    try:
        walkers_snapshot = db.collection('users').where('userType', '==', 'walker').get()
        walkers = [doc.to_dict() for doc in walkers_snapshot]
        return jsonify(walkers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Additional API Endpoints ---
# (Get user details, update profiles, etc.)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True) 