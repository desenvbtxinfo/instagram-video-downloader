from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
import os, tempfile, shutil, threading, time
import yt_dlp

app = Flask(__name__)
# Em produção, restrinja origins ao domínio do seu GitHub Pages.
allowed_origin = os.environ.get("FRONTEND_ORIGIN", "*")
CORS(app, resources={r"/download": {"origins": allowed_origin}})

ALLOWED_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}
MAX_URL_LENGTH = 2000

def valid_instagram_url(value):
    if not isinstance(value, str) or len(value) > MAX_URL_LENGTH:
        return False
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in {"http", "https"} and (parsed.hostname or "").lower() in ALLOWED_HOSTS
    except Exception:
        return False

def remove_later(path, delay=600):
    def cleanup():
        time.sleep(delay)
        shutil.rmtree(path, ignore_errors=True)
    threading.Thread(target=cleanup, daemon=True).start()

@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "instagram-video-backend"})

@app.post("/download")
def download():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    if not valid_instagram_url(url):
        return jsonify({"error": "Insira uma URL válida do Instagram."}), 400

    workdir = tempfile.mkdtemp(prefix="ig_")
    try:
        opts = {
            "outtmpl": os.path.join(workdir, "%(title).80s-%(id)s.%(ext)s"),
            "format": "best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "restrictfilenames": True,
            "socket_timeout": 20,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        candidates = [
            os.path.join(workdir, name) for name in os.listdir(workdir)
            if os.path.isfile(os.path.join(workdir, name))
            and not name.endswith((".part", ".ytdl"))
        ]
        if not candidates:
            raise RuntimeError("Nenhum arquivo de vídeo foi gerado.")
        video = max(candidates, key=os.path.getsize)
        name = secure_filename(os.path.basename(video)) or "video-instagram.mp4"
        response = send_file(video, as_attachment=True, download_name=name)
        remove_later(workdir)
        return response
    except Exception:
        shutil.rmtree(workdir, ignore_errors=True)
        return jsonify({
            "error": "Não foi possível baixar. O vídeo pode ser privado, exigir login, "
                     "estar restrito ou a URL pode estar incorreta."
        }), 422

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
