from dotenv import load_dotenv
from h11 import Response
import os
import requests
import subprocess
import time
from typing import AnyStr, Any
from typing import List

load_dotenv()

TUNNELS: str = "http://127.0.0.1:4040/api/tunnels"
DIRPATH: str = "logs/url/"
CREDURL: str = "https://api.ngrok.com/credentials"

# NGROK Handler
class NGROK:
    def __init__(self):
        global TUNNELS, DIRPATH, CREDURL
        self.tunnels: str = TUNNELS
        self.url_file_path: str = DIRPATH
        self.headers = {
            "Authorization": f"Bearer {self.key_reader}",
            "Ngrok-Version": "2",
            "Content-Type": "application/json"
        }
        self.cred_url = CREDURL
        self.data = {
            "description": "development cred for user"
        }

    def auth_token_creator(self) -> AnyStr:
        response: Any = requests.post(self.cred_url,
                                           headers=self.headers,
                                           json=self.data)
        if response.status_code == 201:
            auth_token: str = response.json()["token"]
            return auth_token
        else:
            return "Unable to Create auth Token"

    def auth_saver(self, filepath: str = ".env"):
        auth_token: str = self.auth_token_creator()
        key: str = "NGROK_AUTH_TOKEN"
        with open(filepath, "r+") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith(key):
                    lines[i] = f"{key}=\"{auth_token}\"\n"
                    break
            else:
                lines.append(f"{key}=\"{auth_token}\"\n")
            f.seek(0)
            f.writelines(lines)
            f.truncate()

    @property
    def key_reader(self) -> AnyStr:
        api_key: str = os.getenv("NGROK_API_KEY")
        return api_key

    @property
    def auth_token_reader(self) -> AnyStr:
        auth_key: str = os.getenv("NGROK_AUTH_TOKEN")
        return auth_key

    def tunnel_killer(self) -> None:
        try:
            response: Any = requests.get(self.tunnels)
            print(response)
            if response.status_code == 200:
                data = response.json()
                for tunnel in data['tunnels']:
                    subprocess.run(["ngrok", "http", "stop", tunnel["name"]], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.STDOUT)
        except requests.ConnectionError:
            print("Bye Bye You've been MOGGED")
        finally:
            return None

    def start_new_tunnel(self) -> None:
        auth_token: str = self.auth_token_reader
        try :
            subprocess.run(["ngrok", "authtoken", auth_token], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.Popen(["ngrok", "start", "--all"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            print("Subprocess error FLAG : calledprocesserror")
        return None

    def get_ngrok_url(self) -> List:
        time.sleep(3)
        try:
            response = requests.get(self.tunnels)
            response.raise_for_status()
            data: dict = response.json()
            ngrok_urls = [tunnel['public_url'] for tunnel in data['tunnels'] if tunnel['proto'] == 'https']
            return ngrok_urls
        except requests.exceptions.RequestException:
            return ["Request error FLAG: 2"]

    def save_ngrok_urls(self, urls: List) -> None:
        if self.url_file_path not in os.listdir():
            os.makedirs(self.url_file_path)
        with open("urls.txt", "w") as f:
            for url  in urls:
                f.write(
                    f"{url}\n"
                )
        return None

    def delete_auths(self) -> AnyStr:
        try:
            response = requests.get(self.cred_url, headers=self.headers)
            response.raise_for_status()
            credentials = response.json().get('credentials', [])
            for credentials in credentials:
                credential_id: str = credentials.get('id')
                del_url: str = f"{self.cred_url}/{credential_id}"
                del_response: Response = requests.delete(del_url, headers=self.headers)
                if del_response.status_code == 204:
                    return f"Deleted url: {del_url}"
                else:
                    return f"Failed to delete: {del_url}"
        except requests.exceptions.RequestException as e:
            return f"Request exception FLAG: 3\n{e}"

    def handle_ngrok(self) -> Any:
        self.auth_saver()
        self.tunnel_killer()
        self.start_new_tunnel()
        self.get_ngrok_url()
        ngrok_urls: List = self.get_ngrok_url()
        self.save_ngrok_urls(urls=ngrok_urls)


if __name__ == "__main__":
    ngrok = NGROK()
    ngrok.handle_ngrok()
