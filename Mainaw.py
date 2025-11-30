# import pyautogui
# import random
# import time


# keys = ['w', 'a', 's', 'd']


# try:
#     while True:
#         key = random.choice(keys)
#         hold_time = random.uniform(1, 5)
        
#         pyautogui.keyDown(key)
#         time.sleep(hold_time)
#         pyautogui.keyUp(key)

#         pause = random.uniform(0.5, 2)
#         time.sleep(pause)

# except KeyboardInterrupt:
#     exit()
# safe_load_test.py
"""
Safe, rate-limited load test sample.
ONLY use against servers you own or have explicit permission to test.
This script includes caps and a rate limiter to reduce accidental harm.
"""

import asyncio
import aiohttp
import time
from typing import Optional

# ----- CONFIGURE BEFORE RUNNING -----
TARGET_URL = "https://www.free4talk.com/"   # <-- CHANGE: must be your target with permission
TOTAL_REQUESTS = 100                  # total requests to perform (hard cap)
CONCURRENCY = 10                      # max number of concurrent requests
REQ_PER_SECOND = 5                    # global requests allowed per second (rate limit)
REQUEST_TIMEOUT = 10                  # seconds
# -----------------------------------

class RateLimiter:
    """Simple token-bucket style rate limiter (async)."""
    def __init__(self, rate: float):
        self.rate = rate  # tokens per second
        self._tokens = rate
        self._last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            # add tokens proportional to elapsed time
            elapsed = now - self._last
            self._tokens = min(self.rate, self._tokens + elapsed * self.rate)
            self._last = now
            if self._tokens < 1:
                # need to wait until at least one token available
                wait_time = (1 - self._tokens) / self.rate
                await asyncio.sleep(wait_time)
                # refill after sleep
                now = time.monotonic()
                elapsed = now - self._last
                self._tokens = min(self.rate, self._tokens + elapsed * self.rate)
                self._last = now
            self._tokens -= 1

async def make_request(session: aiohttp.ClientSession, url: str, idx: int, timeout: int) -> dict:
    try:
        async with session.get(url, timeout=timeout) as resp:
            status = resp.status
            # do not read entire body indiscriminately; we just want status/time
            await resp.content.read(0)
            return {"index": idx, "status": status, "error": None}
    except Exception as e:
        return {"index": idx, "status": None, "error": str(e)}

async def worker(name: int, session: aiohttp.ClientSession, queue: asyncio.Queue, sem: asyncio.Semaphore, rl: RateLimiter, timeout: int, results: list):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        idx, url = item
        await rl.acquire()           # enforce global rate limit
        async with sem:              # enforce concurrency limit
            start = time.monotonic()
            res = await make_request(session, url, idx, timeout)
            elapsed = time.monotonic() - start
            res.update({"elapsed": elapsed})
            results.append(res)
            # lightweight logging
            if res["error"]:
                print(f"[{name}] #{idx} ERROR: {res['error']}")
            else:
                print(f"[{name}] #{idx} -> {res['status']} ({elapsed:.2f}s)")
        queue.task_done()

async def main():
    if TOTAL_REQUESTS <= 0 or CONCURRENCY <= 0 or REQ_PER_SECOND <= 0:
        raise SystemExit("Invalid configuration: all numeric values must be > 0")

    # Build queue of jobs (URL per job)
    queue = asyncio.Queue()
    for i in range(1, TOTAL_REQUESTS + 1):
        queue.put_nowait((i, TARGET_URL))

    # Put sentinel None for each worker to exit cleanly
    sem = asyncio.Semaphore(CONCURRENCY)
    rate_limiter = RateLimiter(REQ_PER_SECOND)
    results = []

    async with aiohttp.ClientSession() as session:
        workers = []
        for w in range(CONCURRENCY):
            workers.append(asyncio.create_task(worker(w+1, session, queue, sem, rate_limiter, REQUEST_TIMEOUT, results)))
        # add sentinel None per worker after queue emptied
        await queue.join()
        for _ in workers:
            await queue.put(None)
        await asyncio.gather(*workers)

    # summary
    success = sum(1 for r in results if r["error"] is None)
    failures = len(results) - success
    avg_time = sum(r["elapsed"] for r in results) / len(results) if results else 0
    print("\n--- SUMMARY ---")
    print(f"Total attempted: {len(results)}")
    print(f"Successes: {success}")
    print(f"Failures: {failures}")
    print(f"Average request time: {avg_time:.2f}s")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Interrupted by user")
