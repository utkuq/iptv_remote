# iptv_remote


``` service
[Unit]
Description=IPTV Remote Flask Server
After=network.target

[Service]
User=utku
WorkingDirectory=/home/{USERNAME}/{DIRECTORY HERE}/iptv_remote
ExecStart=/home/{USERNAME}/{DIRECTORY HERE}/iptv_remote/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target

```

``` shell
sudo systemctl daemon-reload
sudo systemctl enable iptv_remote.service   # her açılışta otomatik başlasın
sudo systemctl start iptv_remote.service    # hemen başlat
sudo systemctl status iptv_remote.service

```