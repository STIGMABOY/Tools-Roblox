from http.server import BaseHTTPRequestHandler
import json, time, hashlib, secrets
from datetime import datetime, timezone

# Admin configuration
ADMIN_CONFIG = {
    'password': 'admin123',  # Password default
    'site_title': 'Robin Cookie Checker Admin'
}

# User database
USER_DB = {
    'testuser': {
        'password': 'test123',
        'expiry': time.time() + 86400 * 30,
        'created': time.time(),
        'plan': 'premium',
        'active': True
    }
}

SESSIONS = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)

class handler(BaseHTTPRequestHandler):
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        path = self.path
        
        if path == '/api/admin/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'success': True,
                'status': 'online',
                'users': len(USER_DB),
                'version': '1.0'
            }).encode())
            
        elif path == '/api/admin/dashboard':
            # Check admin token
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer '):
                self.send_error(401, 'Unauthorized')
                return
            
            token = auth[7:]
            if token not in SESSIONS:
                self.send_error(401, 'Invalid token')
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            active = sum(1 for u in USER_DB.values() if u['active'] and u['expiry'] > time.time())
            expired = len(USER_DB) - active
            
            self.wfile.write(json.dumps({
                'success': True,
                'stats': {
                    'total_users': len(USER_DB),
                    'active_users': active,
                    'expired_users': expired,
                    'today_logins': 0,
                    'memory_usage': 0
                },
                'config': ADMIN_CONFIG
            }).encode())
            
        elif path == '/api/admin/users':
            auth = self.headers.get('Authorization', '')
            if not auth.startswith('Bearer '):
                self.send_error(401, 'Unauthorized')
                return
            
            token = auth[7:]
            if token not in SESSIONS:
                self.send_error(401, 'Invalid token')
                return
            
            users_list = []
            for username, data in USER_DB.items():
                days = max(0, int((data['expiry'] - time.time()) / 86400))
                users_list.append({
                    'username': username,
                    'plan': data['plan'],
                    'active': data['active'] and data['expiry'] > time.time(),
                    'created': data['created'],
                    'created_date': datetime.fromtimestamp(data['created']).strftime('%Y-%m-%d'),
                    'expiry': data['expiry'],
                    'expiry_date': datetime.fromtimestamp(data['expiry']).strftime('%Y-%m-%d'),
                    'days_left': days
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'success': True,
                'users': users_list
            }).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        path = self.path
        
        if path == '/api/admin/login':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                username = data.get('username', '').strip().lower()
                password = data.get('password', '')
                
                print(f"Login attempt: {username}")
                
                # Cek admin login
                if username == 'admin' and password == ADMIN_CONFIG['password']:
                    token = generate_token()
                    SESSIONS[token] = {
                        'username': 'admin',
                        'role': 'admin',
                        'login_time': time.time(),
                        'expiry': time.time() + 86400
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    response = {
                        'success': True,
                        'message': 'Login successful',
                        'token': token,
                        'user': {
                            'username': 'admin',
                            'role': 'admin'
                        }
                    }
                    
                    self.wfile.write(json.dumps(response).encode())
                    
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': 'Invalid username or password'
                    }).encode())
                    
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
                
        elif path == '/api/admin/create_user':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data)
                
                auth = self.headers.get('Authorization', '')
                if not auth.startswith('Bearer '):
                    self.send_error(401, 'Unauthorized')
                    return
                
                token = auth[7:]
                if token not in SESSIONS:
                    self.send_error(401, 'Invalid token')
                    return
                
                username = data.get('username', '').strip().lower()
                password = data.get('password', '')
                days = int(data.get('days', 30))
                
                if not username or not password:
                    self.send_error(400, 'Username and password required')
                    return
                
                if username in USER_DB:
                    self.send_error(400, 'Username already exists')
                    return
                
                USER_DB[username] = {
                    'password': password,
                    'expiry': time.time() + (days * 86400),
                    'created': time.time(),
                    'plan': data.get('plan', 'basic'),
                    'active': True
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': f'User {username} created',
                    'user': {
                        'username': username,
                        'expiry': USER_DB[username]['expiry'],
                        'expiry_date': datetime.fromtimestamp(USER_DB[username]['expiry']).strftime('%Y-%m-%d')
                    }
                }).encode())
                
            except Exception as e:
                self.send_error(500, str(e))
                
        elif path == '/api/admin/logout':
            auth = self.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                token = auth[7:]
                if token in SESSIONS:
                    del SESSIONS[token]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({
                'success': True,
                'message': 'Logged out'
            }).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps({
            'success': False,
            'error': message
        }).encode())
