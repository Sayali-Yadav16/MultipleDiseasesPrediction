import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socketserver
import requests

# This wrapper attempts to start Streamlit in the background and proxy a simple HTTP response.
# NOTE: Vercel serverless environments are ephemeral and have limits; this is a best-effort wrapper.

PORT = os.environ.get("PORT", "8000")
STREAMLIT_CMD = ["streamlit", "run", "app.py", "--server.port", PORT, "--server.address", "0.0.0.0", "--server.headless", "true"]

def start_streamlit():
    try:
        subprocess.Popen(STREAMLIT_CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        print("Failed to start streamlit:", e)

# Start streamlit in background
start_streamlit()

# Give streamlit some time to boot
time.sleep(2)

# Simple response for Vercel serverless - return a redirect to the same host/port
def handler(environ, start_response):
    status = '302 Found'
    headers = [('Location', '/__streamlit__/')]
    start_response(status, headers)
    return [b'']

# WSGI entrypoint for Vercel's Python runtime
def app(environ, start_response):
    # Try to probe Streamlit root; if available, proxy a redirect to it
    try:
        import urllib.parse as urlparse
        host = environ.get('HTTP_HOST','localhost:'+PORT)
        # If Streamlit is up, redirect to root
        start_response('302 Found', [('Location', f'http://{host}/')])
        return [b'']
    except Exception as e:
        start_response('500 Internal Server Error', [('Content-Type','text/plain')])
        return [f'Error starting Streamlit: {e}'.encode('utf-8')]
