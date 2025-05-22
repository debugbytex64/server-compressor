import os
from flask import Flask, request, jsonify, send_from_directory
import mysql.connector

app = Flask(__name__)

# MySQL Database Configuration
db = mysql.connector.connect(
    host="127.0.0.1",
    user="admin",
    password="admin",
    database="server"
)

cursor = db.cursor()

# Home Route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask API!"})

# Upload folder setup
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route to Upload File and Store in MySQL
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided!"}), 400

    file = request.files['file']
    filename = file.filename
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Store File Path in MySQL
    sql = "INSERT INTO users (file_path) VALUES (%s)"
    cursor.execute(sql, (file_path,))
    db.commit()

    return jsonify({"message": "File uploaded successfully!", "file_path": file_path})

# Route to Retrieve File Path from MySQL
#Route to Retrieve File Path from MySQL
@app.route('/file/<int:user_id>', methods=['GET'])
def get_file(user_id):
    sql = "SELECT file_path FROM users WHERE id = %s"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchone()

    if not result:
        return jsonify({"error": "File not found!"}), 404

    file_path = result[0]
    
    if file_path is None:
        return jsonify({"error": "No file path stored for this user!"}), 400

    # Extract the filename from the file path (for serving the file URL)
    filename = os.path.basename(file_path)
    return jsonify({"file_url": f"http://127.0.0.1:5000/uploads/{filename}"})


#Route to Serve Uploaded Files
@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

#Route to List All Uploaded Files
@app.route('/uploads', methods=['GET'])
def list_uploaded_files():
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    file_urls = [
        f"http://127.0.0.1:5000/uploads/{filename}" for filename in files
    ]
    return jsonify({"uploaded_files": file_urls})

if __name__ == '__main__':
    app.run(debug=True)

# curl -X POST -F "file=@C:/Users/tahme/Desktop/server/DSC01095.JPG" http://127.0.0.1:5000/upload
# waitress-serve --listen=127.0.0.1:5000 server:app
# .\nginx.exe -t
# .\nginx.exe -s reload
# .\nginx.exe -s stop


# curl -X POST -F "file=@C:/Users/tahme/Desktop/server/DSC01095.JPG" http://127.0.0.1:5000/upload
# waitress-serve --listen=127.0.0.1:5000 server:app
# .\nginx.exe -t
# .\nginx.exe -s reload
# .\nginx.exe -s stop
