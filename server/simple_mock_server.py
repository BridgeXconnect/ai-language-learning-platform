#!/usr/bin/env python3
"""
Simple mock server for testing frontend integration
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

class MockAPIHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == '/health':
            self._set_headers()
            response = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/auth/profile':
            self._set_headers()
            response = {
                "id": 1,
                "username": "demo_user",
                "email": "demo@example.com",
                "first_name": "Demo",
                "last_name": "User",
                "status": "active",
                "roles": ["sales", "admin"]
            }
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path.startswith('/sales/'):
            self._set_headers()
            response = {"message": "Sales API endpoint (mock)", "data": []}
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self._set_headers(404)
            response = {"error": "Endpoint not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        if self.path == '/auth/login':
            self._set_headers()
            try:
                data = json.loads(post_data)
                response = {
                    "access_token": "mock_access_token_12345",
                    "refresh_token": "mock_refresh_token_67890",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "username": "demo_user",
                        "email": data.get("email", "demo@example.com"),
                        "first_name": "Demo",
                        "last_name": "User",
                        "status": "active",
                        "roles": ["sales", "admin"]
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            except json.JSONDecodeError:
                self._set_headers(400)
                response = {"error": "Invalid JSON"}
                self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/auth/register':
            self._set_headers()
            response = {"message": "User registered successfully", "user_id": 123}
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self._set_headers(404)
            response = {"error": "POST endpoint not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        print(f"🌐 {self.client_address[0]} - {format % args}")

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), MockAPIHandler)
    print(f"🚀 Mock API Server running on http://localhost:{port}")
    print(f"❤️  Health Check: http://localhost:{port}/health")
    print(f"🔐 Login endpoint: POST http://localhost:{port}/auth/login")
    print(f"👤 Profile endpoint: GET http://localhost:{port}/auth/profile")
    print("Press Ctrl+C to stop the server")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Mock server stopped")
        server.shutdown()