from flask import Flask, request, jsonify
from auth_service import create_user, verify_user, list_users, delete_user, update_user, google_sign_in, generate_custom_token

app = Flask(__name__)

@app.route("/create_user", methods=["POST"])
def create_user_endpoint():
    data = request.get_json()  
    email = data.get("email") 
    password = data.get("password")  

    result = create_user(email, password) 
    return jsonify(result)  

@app.route("/verify_user", methods=["GET"])
def verify_user_endpoint():
    email = request.args.get("email") 

    result = verify_user(email)  
    return jsonify(result)  

@app.route("/list_users", methods=["GET"])
def list_users_endpoint():
    result = list_users() 
    return jsonify(result) 


@app.route("/update_user", methods=["PUT"])
def update_user_endpoint():
    data = request.get_json() 
    uid = data.get("uid")  

    if not uid:
        return jsonify({"error": " UID is required!"}), 400

    email = data.get("email")
    password = data.get("password")
    display_name = data.get("display_name")

    result = update_user(uid, email, password, display_name)  
    return jsonify(result) 


@app.route("/delete_user", methods=["DELETE"])
def delete_user_endpoint():
    data = request.get_json() 
    uid = data.get("uid")  

    if not uid:
        return jsonify({"error": "UID is required!"}), 400

    result = delete_user(uid)  
    return jsonify(result)  

@app.route("/google_login", methods=["POST"])
def google_login():
    data = request.get_json()
    id_token = data.get("id_token")  

    if not id_token:
        return jsonify({"error": " ID Token is required!"}), 400

    result = google_sign_in(id_token)  
    return jsonify(result)


@app.route("/generate_token", methods=["POST"])
def generate_token():
    data = request.get_json()
    uid = data.get("uid") 

    if not uid:
        return jsonify({"error": " UID is required!"}), 400

    result = generate_custom_token(uid)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
