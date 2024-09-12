import os
import subprocess
from typing import AnyStr
from pathlib import Path

NGINX_CERT_DIR = "/etc/nginx/certs"
CERT_KEY = os.path.join(NGINX_CERT_DIR, "localhost.direct.key")
CERT_CRT = os.path.join(NGINX_CERT_DIR, "localhost.direct.crt")


class SSLGEN:
    def __init__(self):
        global CERT_CRT, CERT_KEY
        self.cert_key = CERT_KEY
        self.cert_crt = CERT_CRT

    def generate_ssl(self) -> AnyStr:
        if not os.path.exists(CERT_KEY) or not os.path.exists(CERT_CRT):
            print("Generating SSL certificate...")
            Path(NGINX_CERT_DIR).mkdir(parents=True, exist_ok=True)
            subprocess.run([
                "openssl", "req", "-x509", "-nodes", "-days", "365", "-newkey", "rsa:2048",
                "-keyout", self.cert_key, "-out", self.cert_crt, "-subj", "/CN=localhost"
            ])
            return f"SSL certificate generated at {NGINX_CERT_DIR}."
        else:
            return "SSL certificate already exists."

if __name__ == "__main__":
    gen_ssl = SSLGEN()
    gen_ssl.generate_ssl()