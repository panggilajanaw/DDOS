import argparse
import asyncio
import aiohttp
import time
import sys
import signal
import random
from urllib.parse import urlparse
from datetime import datetime

MAX_RPS = 500                
BASE_INTERVAL = 0.1         
BURST_INTERVAL = 0.1    
BURST_DURATION = 300
BURST_EVERY = 0.1
ERROR_CUTOFF = 300        

TIMEOUT = 5
running = True

RESET="\033[0m"; DIM="\033[2m"
G="\033[92m"; R="\033[91m"; C="\033[96m"; Y="\033[93m"
SPIN = ["|","/","-","\\"]

def stop(sig, frm):
    global running
    running = False
    print(f"\n{R}Stopped{RESET}")

signal.signal(signal.SIGINT, stop)

async def chaos_layer():
    r = random.randint(1, 10)
    if r <= 2:
        await asyncio.sleep(2)         
        
    elif r == 10:
        raise asyncio.TimeoutError()   
        
async def run(url, duration):
    start = time.time()
    sent = ok = err = 0
    spin = 0
    last_burst = 0

    timeout = aiohttp.ClientTimeout(total=TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while running:
            elapsed = time.time() - start
            if duration > 0 and elapsed >= duration:
                break

            now = time.time()
            in_burst = (now - last_burst >= BURST_EVERY)
            interval = BURST_INTERVAL if in_burst else BASE_INTERVAL

            if in_burst:
                burst_end = now + BURST_DURATION
                last_burst = now
            else:
                burst_end = None

            try:
                await chaos_layer()
                async with session.get(url) as r:
                    sent += 1
                    if r.status < 400:
                        ok += 1
                    else:
                        err += 1
            except Exception:
                sent += 1
                err += 1

            
            if sent >= 300:
                ratio = err / sent
                if ratio >= ERROR_CUTOFF:
                    print(f"\n{Y}Auto stop:{RESET} error ratio {ratio:.2f}")
                    break

            rps = int(sent / elapsed) if elapsed > 0 else 0
            rps = min(rps, MAX_RPS)

            ts = datetime.now().strftime("%H:%M:%S")
            sys.stdout.write(
                f"\r{DIM}{ts}{RESET} {SPIN[spin%4]} "
                f"sent={sent} ok={G}{ok}{RESET} "
                f"err={R}{err}{RESET} rps={C}{rps}{RESET}"
            )
            sys.stdout.flush()
            spin += 1

            await asyncio.sleep(interval)

            if burst_end and time.time() >= burst_end:
                pass  

    print("\n\nSummary")
    print("-------")
    print("Target :", url)
    print("Sent   :", sent)
    print("OK     :", ok)
    print("Error  :", err)

def main():
    parser = argparse.ArgumentParser(
        description="Availability & resilience testing (localhost only)"
    )
    parser.add_argument(
        "-attack", nargs=2, metavar=("URL","TIME"),
        help="run test (TIME seconds, 0 = unlimited)"
    )
    args = parser.parse_args()

    if args.attack:
        url, t = args.attack
        duration = int(t)

        print("NAWW Test Engine")
        print("----------------")
        print("Target :", url)
        print("Mode   : load + burst + chaos (safe)")
        print("Scope  : localhost only")
        print("Time   :", "unlimited" if duration == 0 else f"{duration}s")
        print("")
        asyncio.run(run(url, duration))
        return

    parser.print_help()

if __name__ == "__main__":
    main()