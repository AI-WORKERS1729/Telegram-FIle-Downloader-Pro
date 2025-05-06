from flask import Flask, render_template, send_from_directory
import os
from pathlib import Path
from datetime import datetime
import math

app = Flask(__name__)
DOWNLOADS_DIR = Path("downloads")
DOWNLOADS_DIR.mkdir(exist_ok=True)

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = int(math.log(size_bytes, 1024))
    return f"{size_bytes/1024**i:.2f} {units[i]}"

@app.route("/")
def index():
    files = []
    for file in DOWNLOADS_DIR.iterdir():
        if file.is_file():
            stat = file.stat()
            files.append({
                "name": file.name,
                "size": convert_size(stat.st_size),
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "type": file.suffix[1:].upper() if file.suffix else "FILE"
            })
    total_size = sum(file.stat().st_size for file in DOWNLOADS_DIR.iterdir() if file.is_file())
    return render_template("index.html", files=files, total_size=convert_size(total_size))

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOADS_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)