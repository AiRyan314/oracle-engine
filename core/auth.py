"""Custom JWT Implementation from scratch using HMAC and SHA256."""
import hmac
import hashlib
import base64
import json
import time

SECRET_KEY = b"ORACLE_ENGINE_SUPER_SECRET_KEY_2026"

def base64url_encode(data: bytes) -> str:
    """Encode bytes to base64url string."""
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    """Decode base64url string to bytes."""
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_jwt(payload: dict, expires_in: int = 3600) -> str:
    """Generate a signed JWT token valid for expires_in seconds."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload["exp"] = int(time.time()) + expires_in
    
    header_enc = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_enc = base64url_encode(json.dumps(payload).encode('utf-8'))
    
    signature = hmac.new(
        SECRET_KEY, 
        f"{header_enc}.{payload_enc}".encode('utf-8'), 
        hashlib.sha256
    ).digest()
    
    sig_enc = base64url_encode(signature)
    return f"{header_enc}.{payload_enc}.{sig_enc}"

def verify_jwt(token: str) -> dict:
    """Verify JWT signature and expiration. Returns payload or raises Exception."""
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("Invalid token format")
        
    header_enc, payload_enc, sig_enc = parts
    
    expected_sig = base64url_encode(hmac.new(
        SECRET_KEY, 
        f"{header_enc}.{payload_enc}".encode('utf-8'), 
        hashlib.sha256
    ).digest())
    
    if not hmac.compare_digest(sig_enc, expected_sig):
        raise ValueError("Invalid signature")
        
    payload = json.loads(base64url_decode(payload_enc).decode('utf-8'))
    if payload.get("exp", 0) < time.time():
        raise ValueError("Token expired")
        
    return payload
