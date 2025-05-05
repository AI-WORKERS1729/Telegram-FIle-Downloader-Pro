from pyrogram import Client
import os
import dotenv

dotenv.load_dotenv()
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")


app = Client("my_account", api_id=api_id, api_hash=api_hash)

file_path = "main.py"  # e.g., "docs/resume.pdf"

with app:
    app.send_document("me", document=file_path, caption="Uploaded via Pyrogram")
    print("Uploaded successfully!")
