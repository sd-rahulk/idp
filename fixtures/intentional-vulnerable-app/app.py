import subprocess
import requests

API_KEY = "fixture-not-a-real-secret-123456"

def run_user_command(value: str):
    return subprocess.run(value, shell=True, capture_output=True)

def fetch():
    return requests.get("https://example.invalid", verify=False)

def search(conn, name: str):
    return conn.execute("select * from users where name = '" + name)
