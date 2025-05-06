from pyrogram import Client
import os
import time
from tqdm import tqdm
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()
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

# Utility to parse index input like "1,3-5"
def parse_indices(input_str, max_index):
    result = set()
    parts = input_str.split(',')
    for part in parts:
        if '-' in part:
            start, end = part.split('-')
            try:
                start, end = int(start), int(end)
                result.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                result.add(int(part))
            except ValueError:
                continue
    return sorted(i for i in result if 0 <= i <= max_index)

# Start Pyrogram session
app = Client("my_account", api_id=api_id, api_hash=api_hash)

with app:
    print("Choose an option:\n1. Download specific file(s) from Saved Messages\n2. Upload a file to Saved Messages")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("Searching for recent media in Saved Messages...")
        messages = app.get_chat_history("me", limit=50)
        media_messages = []

        for i, msg in enumerate(messages):
            if msg.document or msg.video or msg.audio:
                media_messages.append(msg)
                file_name = msg.document.file_name if msg.document else "Video/Audio"
                file_size = msg.document.file_size if msg.document else 0
                print(f"[{len(media_messages) - 1}] {file_name} ({file_size / (1024*1024):.2f} MB)")

        if not media_messages:
            print("No downloadable media found.")
        else:
            selection = input("Enter index/indices or range (e.g., 0,2,4-6): ").strip()
            indices = parse_indices(selection, len(media_messages) - 1)

            if not indices:
                print("No valid indices selected.")
            else:
                for idx in indices:
                    msg = media_messages[idx]
                    print(f"\nDownloading: {msg.document.file_name if msg.document else 'Media'}")
                    pbar = None
                    downloaded_path = app.download_media(msg, progress=progress)
                    if pbar:
                        pbar.close()
                    print(f"Downloaded to: {downloaded_path}")

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
