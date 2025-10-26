from flask import Flask, render_template, request, redirect, url_for
import requests
import subprocess
import re
import json
import os

app = Flask(__name__)
CONFIG_FILE = "iptv_config.json"

class IPTV:
    def __init__(self):
        self.iptv_link = None
        self.channels = []
        self.load_config()
        if self.iptv_link:
            try:
                self.get_channels()
            except Exception as e:
                print(f"Kanal yüklenirken hata: {e}")

    # 🔹 Config yükleme (boş dosya veya hatalı JSON durumunda güvenli)
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self.save_config()
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.iptv_link = data.get("iptv_link")
                except (json.JSONDecodeError, ValueError):
                    self.iptv_link = None
                    self.save_config()
        except Exception as e:
            print(f"Config yüklenemedi: {e}")
            self.iptv_link = None

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump({"iptv_link": self.iptv_link}, f)
        except Exception as e:
            print(f"Config kaydedilemedi: {e}")

    def get_channels(self):
        if not self.iptv_link:
            return

        response = requests.get(self.iptv_link, timeout=10)
        response.raise_for_status()
        lines = response.text.splitlines()
        self.channels = []

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                name_match = re.search(r',(.+)$', lines[i])
                channel_name = name_match.group(1).strip() if name_match else "Bilinmeyen Kanal"

                channel_url = lines[i + 1].strip() if i + 1 < len(lines) and lines[i + 1].startswith("http") else None
                
                group_match = re.search(r'group-title="([^"]+)"', lines[i])
                country = group_match.group(1) if group_match else "Unknown"

                if channel_url:
                    self.channels.append({
                        "name": channel_name,
                        "url": channel_url,
                        "country": country
                    })

    def play_channel(self, channel_url):
        if channel_url:
            try:
                subprocess.Popen(["cvlc", channel_url])
            except FileNotFoundError:
                print("VLC bulunamadı. Lütfen cVLC'nin PATH'te olduğundan emin olun.")

iptv = IPTV()

@app.route("/", methods=["GET", "POST"])
def index():
    show_form = False
    if request.method == "POST":
        new_link = request.form.get("iptv_link_input")
        if new_link:
            iptv.iptv_link = new_link
            iptv.save_config()
            iptv.get_channels()
    # Eğer configte link yoksa veya kullanıcı değiştirmek isterse form göster
    if not iptv.iptv_link:
        show_form = True
    return render_template("index.html", channels=iptv.channels, show_form=show_form)

@app.route("/watch")
def watch():
    channel_url = request.args.get("channel_url")
    if channel_url:
        iptv.play_channel(channel_url)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
