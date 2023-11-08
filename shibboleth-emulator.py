from flask import Flask, request, render_template, Response
import config
import requests

app = Flask(__name__)

# Keep the most recent headers for the shibboleth page to make incremental changes easier
last_headers = config.SHIBBOLETH_HEADERS.copy()
last_method: str = "POST"


def handle_shibboleth(path: str):
    global last_method
    complete: bool = request.args.get("shibboleth_proxy_complete", None) is not None
    if complete:
        # Pass through to the real server with the Shibboleth headers

        add_headers = {
            "Shib-Cookie-Name": "",
            "Shib-Session-Id": "",
            "Shib-Session-Index": "",
            "Shib-Session-Expires": "",
            "Shib-Session-Inactivity": "",
            "Shib-Identity-Provider": "",
            "Shib-Authentication-Method": "",
            "Shib-Authentication-Instant": "",
            "Shib-Authncontext-Class": "",
            "Shib-Authncontext-Decl": "",
            "Shib-Assertion-Count": "",
            "Shib-Handler": "",
            "Shib-Application-Id": ""
        }

        for header, value in last_headers.items():
            query_value: str = request.args.get(header, None)
            if query_value is not None:
                last_headers[header] = query_value

        add_headers |= last_headers

        last_method = request.args.get("method", "POST")

        return handle_passthrough(path, add_headers, last_method)

    else:
        # Render a page where the user can fill out the headers to spoof and then continue to the real server
        return render_template("shibboleth.html", path=path, method=last_method, headers=last_headers)


def handle_passthrough(path: str, add_headers: dict = None, method: str = None):
    # Based on https://stackoverflow.com/a/36601467
    r = request
    url = config.PASSTHROUGH_URL + path
    new_headers = {k: v for k, v in r.headers}
    new_headers["X-Forwarded-For"] = r.remote_addr
    if add_headers is not None:
        new_headers |= add_headers
    if config.EMULATE_HOST:
        new_headers["Host"] = config.EMULATE_HOST_VALUE
    backend_response = requests.request(
        method=method or r.method,
        url=url,
        headers=new_headers,
        data=r.get_data(),
        cookies=r.cookies,
        allow_redirects=False
    )
    response_headers = dict(backend_response.headers.items())

    # Replace links to the passthrough URL with links to the emulator URL
    if config.REPLACE_URLS:
        new_content = backend_response.content.replace(config.PASSTHROUGH_URL.encode(), r.host_url.encode()[:-1])
    else:
        new_content = backend_response.content
    proxy_response = Response(new_content, backend_response.status_code, response_headers)

    # Set cookies
    for cookie in backend_response.cookies:
        proxy_response.set_cookie(cookie.name, cookie.value, path=cookie.path, secure=cookie.secure,
                                  httponly="HttpOnly" in cookie.__dict__.get("_rest", {}),
                                  domain=cookie.domain, expires=cookie.expires)

    # Remove invalid headers
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    for header in excluded_headers:
        proxy_response.headers.pop(header, None)

    return proxy_response


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS", "CONNECT", "TRACE"])
def index(path):
    # Argument path doesn't include the prefix slash, so replace it
    r = request
    path = r.path
    if path in config.SHIBBOLETH_PATHS:
        return handle_shibboleth(path)
    return handle_passthrough(path)


def main():
    app.run(host=config.HOST, port=config.PORT, debug=True)


if __name__ == '__main__':
    main()
