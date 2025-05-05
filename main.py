from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pyrogram import Client
import os
import dotenv
import shutil
import asyncio

dotenv.load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
SESSION_DIR = "sessions"

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

active_clients = {}

async def create_client(phone):
    client = Client(phone, api_id=api_id, api_hash=api_hash, workdir=SESSION_DIR)
    return client

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start", methods=["POST"])
async def start():
    phone = request.json["phone"]
    client = await create_client(phone)
    try:
        await client.connect()
        sent_code = await client.send_code(phone)
        print(f"Sent code response: {sent_code}")  # Debugging log
        await client.disconnect()
        return jsonify({"status": "code_sent", "phone_code_hash": sent_code.phone_code_hash})
    except Exception as e:
        print(f"Error in /start: {e}")  # Debugging log
        return jsonify({"error": str(e)}), 400

@app.route("/verify", methods=["POST"])
async def verify():
    data = request.json
    print(f"Incoming request data: {data}")  # Debugging log

    phone = data.get("phone")
    code = data.get("code")
    phone_code_hash = data.get("phone_code_hash")

    if not phone or not code or not phone_code_hash:
        return jsonify({"error": "Missing required fields"}), 400

    client = await create_client(phone)
    try:
        await client.connect()
        await client.sign_in(phone,phone_code_hash,code)
        active_clients[phone] = client
        return jsonify({"status": "verified"})
    except Exception as e:
        print(f"Error in /verify: {e}")  # Debugging log
        if "PHONE_CODE_EXPIRED" in str(e):
            return jsonify({"error": "The confirmation code has expired. Please request a new code."}), 400
        await client.disconnect()
        return jsonify({"error": str(e)}), 400

@app.route("/upload", methods=["POST"])
async def upload():
    phone = request.args.get("phone")
    if phone not in active_clients:
        return jsonify({"error": "Not authenticated"}), 403

    file = request.files["file"]
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)
    client = active_clients[phone]
    await client.send_document("me", document=filepath, caption=file.filename)
    os.remove(filepath)
    return jsonify({"status": "uploaded"})

@app.route("/list", methods=["GET"])
async def list_files():
    phone = request.args.get("phone")
    if phone not in active_clients:
        return jsonify([])

    client = active_clients[phone]
    msgs = await client.get_chat_history("me", limit=10)
    files = [{"name": msg.document.file_name, "url": msg.document.file_id} for msg in msgs if msg.document]
    return jsonify(files)

@app.route("/logout", methods=["POST"])
async def logout():
    phone = request.args.get("phone")
    if phone in active_clients:
        client = active_clients.pop(phone)
        await client.stop()
        shutil.rmtree(os.path.join(SESSION_DIR, phone), ignore_errors=True)
    return jsonify({"status": "logged_out"})

if __name__ == "__main__":
    app.run(debug=True, port=10000)
