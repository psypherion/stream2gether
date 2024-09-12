import os
import subprocess
from typing import Any
from ngrok_handler import NGROK
from sslGen import SSLGEN

NGINX_CONFIG: str = "/etc/nginx/sites-available/ngrok.conf"
NGINX_CERT_DIR: str = "/etc/nginx/certs"
CERT_KEY: str = os.path.join(NGINX_CERT_DIR, "localhost.direct.key")
CERT_CRT: str = os.path.join(NGINX_CERT_DIR, "localhost.direct.crt")
NGROK_TUNNELS: str = "http://127.0.0.1:4040/api/tunnels"
NGROK_LOCAL: str = "ngrok.localhost.direct"


class Nginx:
    def __init__(self, ngrok_url: str):
        global NGINX_CONFIG, NGROK_TUNNELS, NGROK_LOCAL, CERT_CRT, CERT_KEY
        self.tunnels = NGROK_TUNNELS
        self.local_ngrok = NGROK_LOCAL
        self.cert_crt = CERT_CRT
        self.cert_key = CERT_KEY
        self.ngrok_url = ngrok_url
        self.nginx_config = NGINX_CONFIG

    def configure_nginx(self):
        nginx_config_content: str= f"""
        server {{
            server_name localhost {self.local_ngrok};

            listen 80;
            listen 443 ssl;

            ssl_certificate {self.cert_crt};
            ssl_certificate_key {self.cert_key};

            location / {{
                # Forward headers
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_set_header Host {self.ngrok_url[8:]};

                # This line bypasses Ngrok's warning
                proxy_set_header ngrok-skip-browser-warning 1;

                # Forward the request to Ngrok
                proxy_pass {self.ngrok_url};

                # Handle SSL
                proxy_ssl_server_name on;
                proxy_ssl_verify off;
            }}
        }}
        """
        with open(self.nginx_config, "w") as f:
            f.write(nginx_config_content)

    def enable_nginx_config(self):
        try:
            self.configure_nginx()
            subprocess.run(["ln", "-sf", self.nginx_config, "/etc/nginx/sites-enabled/ngrok.conf"])
        except subprocess.CalledProcessError as e:
            print("Command failed with exit code", e.returncode)
            print("Error output:", e.stderr.decode())

    @staticmethod
    def reload_nginx():
        result: Any = subprocess.run(["nginx", "-t"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("Reloading Nginx...")
            subprocess.run(["systemctl", "reload", "nginx"])
            print("Nginx reloaded successfully.")
        else:
            print("Nginx configuration test failed!")
            print(result.stderr.decode())
            exit(1)

    def handle_nginx(self):
        ssl = SSLGEN()
        ssl.generate_ssl()
        self.enable_nginx_config()
        self.reload_nginx()

if __name__ == "__main__":
    ngrok = NGROK()
    ngrok.handle_ngrok()
    ngrok_urls = ngrok.get_ngrok_url()[0]
    nginx = Nginx(ngrok_url=ngrok_urls)
    nginx.handle_nginx()