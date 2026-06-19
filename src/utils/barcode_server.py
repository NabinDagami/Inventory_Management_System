import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

SCANNER_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Barcode Scanner</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #eee;
         display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 16px; }
  h2 { margin: 20px 0 10px; color: #60a5fa; }
  p { color: #999; font-size: 14px; margin-bottom: 16px; text-align: center; }
  video { width: 100%; max-width: 500px; border-radius: 12px; background: #000; }
  #result { margin-top: 16px; font-size: 24px; font-weight: bold; color: #4ade80;
            word-break: break-all; text-align: center; min-height: 40px; }
  #status { margin-top: 12px; font-size: 13px; color: #888; }
  #reader { width: 100%; max-width: 500px; border-radius: 12px; overflow: hidden;
            background: #16213e; padding: 8px; display: none; }
</style>
</head>
<body>
  <h2>Barcode Scanner</h2>
  <p>Point your camera at a barcode.</p>
  <video id="video" autoplay playsinline></video>
  <div id="reader"></div>
  <div id="result"></div>
  <div id="status">Loading camera...</div>

  <script>
    const video = document.getElementById('video');
    const reader = document.getElementById('reader');
    const resultEl = document.getElementById('result');
    const statusEl = document.getElementById('status');
    let lastCode = '';
    let scanning = false;

    async function sendBarcode(code) {
      if (code === lastCode) return;
      lastCode = code;
      resultEl.textContent = '\u2705 ' + code;
      statusEl.textContent = 'Sending to app...';
      try {
        await fetch('/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ barcode: code })
        });
        statusEl.textContent = '\u2713 Sent! Ready for next scan.';
        setTimeout(() => { statusEl.textContent = 'Ready.'; }, 1500);
      } catch {
        statusEl.textContent = '\u274c Failed to send.';
      }
    }

    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 640 }, height: { ideal: 480 } }
        });
        video.srcObject = stream;
        await video.play();

        if ('BarcodeDetector' in window) {
          statusEl.textContent = 'Using native barcode detector...';
          startNativeDetection();
        } else {
          statusEl.textContent = 'Loading scanner library...';
          video.style.display = 'none';
          reader.style.display = 'block';
          stream.getTracks().forEach(t => t.stop());
          startFallbackScanner();
        }
      } catch (err) {
        statusEl.textContent = '\u274c Camera error: ' + err.message;
      }
    }

    async function startNativeDetection() {
      let detector;
      try {
        detector = new BarcodeDetector({
          formats: ['ean_13','ean_8','upc_a','upc_e','code_39','code_128','itf','qr_code','data_matrix','aztec']
        });
      } catch {
        statusEl.textContent = 'Native detector not available, loading fallback...';
        video.style.display = 'none';
        reader.style.display = 'block';
        video.srcObject.getTracks().forEach(t => t.stop());
        startFallbackScanner();
        return;
      }

      statusEl.textContent = 'Camera active \u2014 scan a barcode.';
      scanning = true;

      async function detect() {
        if (!scanning) return;
        try {
          const barcodes = await detector.detect(video);
          for (const b of barcodes) {
            await sendBarcode(b.rawValue);
          }
        } catch {}
        requestAnimationFrame(detect);
      }
      detect();
    }

    function startFallbackScanner() {
      const script = document.createElement('script');
      script.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';
      script.onload = () => {
        const html5QrCode = new Html5Qrcode('reader');
        html5QrCode.start(
          { facingMode: 'environment' },
          { fps: 10, qrbox: { width: 350, height: 100 } },
          (text) => sendBarcode(text)
        ).then(() => {
          statusEl.textContent = 'Camera active \u2014 scan a barcode.';
        }).catch(err => {
          statusEl.textContent = '\u274c Scanner error: ' + err;
        });
      };
      script.onerror = () => {
        statusEl.textContent = '\u274c Failed to load scanner library. Check internet connection.';
      };
      document.body.appendChild(script);
    }

    startCamera();
  </script>
</body>
</html>"""


class BarcodeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(SCANNER_PAGE.encode('utf-8'))

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/scan':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            code = data.get('barcode', '')

            if code and getattr(self.server, "callback", None):
                # Server-side debounce to prevent repeated increments from scanner bursts
                now_ms = int(time.time() * 1000)
                last_code = getattr(self.server, "_last_code", None)
                last_ts_ms = getattr(self.server, "_last_ts_ms", 0)
                debounce_ms = getattr(self.server, "_scan_debounce_ms", 1200)

                if code == last_code and (now_ms - last_ts_ms) < debounce_ms:
                    pass
                else:
                    self.server._last_code = code
                    self.server._last_ts_ms = now_ms
                    self.server.callback(code)

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass


class BarcodeServer:
    def __init__(self, host='0.0.0.0', port=8765):
        self.host = host
        self.port = port
        self.callback = None
        self._server = None
        self._thread = None

        # Debounce state (prevents same barcode being processed multiple times)
        self._last_code = None
        self._last_ts_ms = 0
        self._scan_debounce_ms = 1200

    def start(self, callback):
        self.callback = callback
        self._server = HTTPServer((self.host, self.port), BarcodeHandler)
        self._server.callback = callback
        self._thread = threading.Thread(target=self._server.serve_forever,
                                        daemon=True)
        self._thread.start()

    @property
    def url(self):
        import socket
        hostname = socket.gethostbyname(socket.gethostname())
        return f"http://{hostname}:{self.port}"

    def stop(self):
        if self._server:
            self._server.shutdown()

