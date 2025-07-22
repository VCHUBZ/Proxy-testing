import requests
from flask import Flask, request, Response

app = Flask(__name__)

TARGET_BASE_URL = "http://213.142.135.46:9999"

@app.before_request
def proxy_request():
    try:
        resp = requests.request(
            method=request.method,
            url=TARGET_BASE_URL + request.full_path.rstrip('?'),
            headers={key: value for key, value in request.headers if key.lower() != 'host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
        )

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items()
                   if name.lower() not in excluded_headers]

        response = Response(resp.content, resp.status_code, headers)
        return response

    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}", 502
