import asyncio
from dynamic_measurement import apply_measurement_to_async_methods
from measure_action import measure_action

# IMPORT FROM LOCAL FOLDER
from reviews.analysis_with_cache import process_models_with_cache
from reviews.analysis_without_cache import process_models_without_cache

from Laptop_Bot import run_query
from Laptop_Bot_optimised import run_query_optimised

from db_mongo import store_laptop_recommendations

class FunctionActions:
    def __init__(self, locust_user):
        self.locust_user = locust_user

    async def analyze_reviews_with_cache(self, models_list):
        # DIRECT AWAIT (No to_thread needed anymore)
        result = await process_models_with_cache(models_list)
        return result
    async def analyze_reviews_without_cache(self, models_list):
        # DIRECT AWAIT (No to_thread needed anymore)
        result = await process_models_without_cache(models_list)
        return result
    
    async def get_laptops(self, query):
        # run_query is blocking. We offload it to a thread.
        # This fixes the "NoneType can't be used in await" error.
        result = await asyncio.to_thread(run_query, query)
        return result
    
    async def get_laptops_optimised(self, query):
        # run_query_optimised is blocking. We offload it to a thread.
        result = await asyncio.to_thread(run_query_optimised, query)
        return result
    
    async def store_laptop_recommendations(self, request_id, items, query_str, user_id=None):
        # store_laptop_recommendations is blocking. We offload it to a thread.
        result = await asyncio.to_thread(store_laptop_recommendations, request_id, items, query_str, user_id)
        return result

apply_measurement_to_async_methods(FunctionActions, measure_action)