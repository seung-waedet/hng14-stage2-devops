import redis
import time
import os
import signal
import sys

shutdown_requested = False

def get_redis_client():
    return redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(2)  # simulate work
    r = get_redis_client()
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")

def signal_handler(signum, frame):
    global shutdown_requested
    print("Received shutdown signal, finishing current job...")
    shutdown_requested = True

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    while not shutdown_requested:
        try:
            r = get_redis_client()
            print("Worker ready, waiting for jobs...")
            job = r.brpop("job", timeout=5)
            if job and not shutdown_requested:
                _, job_id = job
                process_job(job_id.decode())
        except redis.exceptions.ConnectionError as e:
            print(f"Redis connection error: {e}, retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}, retrying in 5 seconds...")
            time.sleep(5)

    print("Worker shutting down gracefully")

if __name__ == "__main__":
    main()