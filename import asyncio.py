import asyncio
import threading
import time

# --- AsyncIO-based API ---
async def fetch_data(name, delay):
    print(f"[{name}] Starting fetch...")
    await asyncio.sleep(delay)
    print(f"[{name}] Finished fetch after {delay}s")
    return f"Data from {name}"

# --- Thread target function ---
def run_in_thread(loop, name, delay):
    # Schedule the coroutine in the event loop running in another thread
    future = asyncio.run_coroutine_threadsafe(fetch_data(name, delay), loop)
    result = future.result()  # Blocks until the coroutine completes
    print(f"[{name}] Result: {result}")

# --- Main event loop thread ---
def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# --- Main program ---
if __name__ == "__main__":
    # Create a new event loop and run it in a separate thread
    loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
    loop_thread.start()

    # Start multiple threads that use the async API
    threads = []
    for i in range(3):
        t = threading.Thread(target=run_in_thread, args=(loop, f"Thread-{i+1}", i+1))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Stop the event loop
    loop.call_soon_threadsafe(loop.stop)
    loop_thread.join()