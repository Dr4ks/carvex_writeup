from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("[+] Headers:\n", self.headers)  # check User-Agent here too
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"SSRF_TEST_12345")

HTTPServer(('0.0.0.0', 1337), Handler).serve_forever()