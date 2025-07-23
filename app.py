import requests
from flask import Flask, request, Response, abort

app = Flask(__name__)

PROXY_TARGET = "http://213.142.135.46:9999"

def proxy_request(path: str):
    url = f"{PROXY_TARGET}{path}"
    headers = {k: v for k, v in request.headers if k.lower() != "host"}

    try:
        resp = requests.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data() if not request.is_json else None,
            json=request.get_json(silent=True) if request.is_json else None,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True,
            timeout=10  # optional: prevent hanging requests
        )
    except requests.RequestException as e:
        app.logger.error(f"Proxy error: {e}")
        return Response(f"Upstream request failed: {e}", status=502)

    # Filter out hop-by-hop headers as per RFC 7230 section 6.1
    excluded_headers = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade"
    }

    response = Response(resp.content, status=resp.status_code)
    for k, v in resp.headers.items():
        if k.lower() not in excluded_headers:
            response.headers[k] = v

    return response

@app.route('/', defaults={'path': ''}, methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
@app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
def catch_all(path):
    full_path = request.full_path if request.query_string else request.path
    return proxy_request(full_path)

if __name__ == "__main__":
    app.run(debug=True)
