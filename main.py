from pyrogram import Client
import os
import time
from tqdm import tqdm
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
# Replace with your credentials
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")

# Global progress bar variables
pbar = None
last_update_time = 0
last_bytes = 0

# Progress callback using tqdm
def progress(current, total):
    global pbar, last_update_time, last_bytes

    now = time.time()
    if not pbar:
        pbar = tqdm(total=total, unit='B', unit_scale=True, desc="Progress")

    if now - last_update_time >= 0.5:
        delta_bytes = current - last_bytes
        delta_time = now - last_update_time
        speed = delta_bytes / delta_time if delta_time else 0
        eta = (total - current) / speed if speed else float('inf')
        pbar.set_postfix(speed=f"{speed / 1024:.2f} KB/s", eta=f"{int(eta)}s")
        last_update_time = now
        last_bytes = current

    pbar.n = current
    pbar.refresh()

# Start Pyrogram session
app = Client("my_account", api_id=api_id, api_hash=api_hash)

with app:
    print("Choose an option:\n1. Download latest file from Saved Messages\n2. Upload a file to Saved Messages")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("Searching for recent media in Saved Messages...")
        messages = app.get_chat_history("me", limit=20)
        target_message = None
        for msg in messages:
            if msg.document or msg.video or msg.audio:
                target_message = msg
                break

        if target_message:
            print("Media found. Starting download...")
            pbar = None
            downloaded_path = app.download_media(target_message, progress=progress)
            if pbar:
                pbar.close()
            print(f"\nDownloaded to: {downloaded_path}")
        else:
            print("No downloadable media found in recent messages.")

    elif choice == "2":
        file_path = input("Enter the full path of the file to upload: ").strip()

        if os.path.exists(file_path) and os.path.isfile(file_path):
            print("Starting upload...")
            pbar = None
            app.send_document("me", document=file_path, caption="Uploaded via Pyrogram", progress=progress)
            if pbar:
                pbar.close()
            print("\nUploaded successfully!")
        else:
            print("Invalid file path. Please check and try again.")

    else:
        print("Invalid option. Please enter 1 or 2.")
