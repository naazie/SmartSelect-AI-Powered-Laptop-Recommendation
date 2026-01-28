import asyncio
import threading
import os
import random
import string
from locust import task, between, User
from function_actions import FunctionActions
import gevent

# --- Async Boilerplate ---
def thread_func(loop, coro, *args, **kwargs):
    future = asyncio.run_coroutine_threadsafe(coro(*args, **kwargs), loop)
    event = gevent.event.Event()
    future.add_done_callback(lambda _: event.set())
    event.wait()
    return future.result()

def run_asyncio(loop, coro, *args, **kwargs):
    return thread_func(loop, coro, *args, **kwargs)

class FunctionUser(User):
    print("Locust class 'Function User' initialized.")
    wait_time = between(2, 5)
    host = "http://localhost"

    shared_loop = None
    shared_thread = None
    initialized_pid = None

    # --- FILTERED DATASET (Lenovo Only) ---
    dataset = [
        "Lenovo IdeaPad Slim 5", "Lenovo ThinkBook 14s", "Lenovo Yoga Slim 7i",
        "Lenovo IdeaPad Slim 3", "Lenovo Legion 5", "Lenovo IdeaPad Flex 5",
        "Lenovo ThinkPad X1 Carbon", "Lenovo LOQ 15", "Lenovo Yoga 9i",
        "Lenovo Legion 7i", "Lenovo ThinkPad T14 Gen 4", "Lenovo IdeaPad Gaming 3"
    ]
    query = "use_case: For everyday tasks (browsing, movies, office work) ; budget: ₹80,000 – ₹1,20,000 (High-end use) ; processor: Powerful – for heavy work or gaming (Intel i7 / Ryzen 7 or above) ; ram: 16GB (Best for multitasking and coding) ; gpu: No, normal use is fine ; screen_size: Standard (15–16 inches, balanced size) ; battery: Mostly use plugged in (not important) ; weight: Medium (1.6–2.5 kg, balanced) ; priorities: Fast performance ; other_requirements: no"

    params = ['6929e58cab0f9dc5f99263d8', [{'model': 'Lenovo Legion Slim 5', 'price_inr': '₹1,35,000', 'why': 'Offers great gaming power with a strong processor and graphics card, making it ideal for your demanding tasks and entertainment.'}, {'model': 'Lenovo Yoga Slim 7 Pro', 'price_inr': '₹1,30,000', 'why': 'This laptop delivers a premium experience with its stunning display and smooth performance, perfect for both work and media consumption.'}, {'model': 'Lenovo ThinkBook 16p Gen 3', 'price_inr': '₹1,40,000', 'why': 'Built for professionals, it boasts powerful specs for seamless multitasking and a vibrant screen for an enjoyable viewing experience.'}, {'model': 'Lenovo IdeaPad Pro 5', 'price_inr': '₹1,32,000', 'why': 'Its balance of performance and display quality makes it excellent for everyday use, creative work, and watching movies with clarity.'}, {'model': 'Lenovo Legion 5 Pro', 'price_inr': '₹1,38,000', 'why': 'This powerful machine excels in gaming and video editing, offering a top-notch visual experience for all your high-demand needs.'}], 'use_case: For everyday tasks (browsing, movies, office work) ; budget: Above ₹1,30,000 (Premium laptops) ; processor: Medium – for smooth multitasking (Intel i5 / Ryzen 5) ; ram: 16GB (Best for multitasking and coding) ; gpu: Yes, for gaming, video editing, or graphics-heavy work ; screen_size: Standard (15–16 inches, balanced size) ; battery: Average battery is fine (5–7 hours) ; weight: Doesn’t matter to me ; priorities: Fast performance, Good display quality, Long battery life, Lightweight and portable', '68fa16f36eecfbbfabf1e043']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_pid = os.getpid()
        if FunctionUser.initialized_pid != current_pid:
            FunctionUser.initialized_pid = current_pid
            FunctionUser.shared_loop = asyncio.new_event_loop()
            FunctionUser.shared_thread = threading.Thread(
                target=FunctionUser.shared_loop.run_forever,
                daemon=True
            )
            FunctionUser.shared_thread.start()

        self.loop = FunctionUser.shared_loop
        self.actions = FunctionActions(self)
   
    @task(1)
    def task_get_reviews_with_cache(self):
        # Pick a random Lenovo model
        target_model = random.choice(self.dataset)

        run_asyncio(self.loop, self.actions.analyze_reviews_with_cache, [target_model])
    
    @task(1)
    def task_get_reviews_without_cache(self):
        # Pick a random Lenovo model
        target_model = random.choice(self.dataset)

        run_asyncio(self.loop, self.actions.analyze_reviews_without_cache, [target_model])

    @task(1)
    def task_get_laptops(self):
        run_asyncio(self.loop, self.actions.get_laptops, self.query)

    @task(1)
    def task_get_laptops_optimised(self):
        run_asyncio(self.loop, self.actions.get_laptops_optimised, self.query)

    @task(1)
    def task_store_laptop_recommendations(self):
        run_asyncio(self.loop, self.actions.store_laptop_recommendations, *self.params)