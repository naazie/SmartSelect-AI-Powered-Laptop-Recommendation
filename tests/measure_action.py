import time

def measure_action(name: str):
    def decorator(func):
        async def wrapper(instance, *args, **kwargs):
            locust_user_instance = instance.locust_user

            start_time = time.time()
            exception = None
            result = None
            try:
                result = await func(instance, *args, **kwargs)
            except Exception as e:
                exception = e
            finally:
                duration = (time.time() - start_time) * 1000
 
                request_type = "custom_action"
                context = {}

                if locust_user_instance.__class__.__name__ == 'UIUser':
                    request_type = "UI_action"
                    context = locust_user_instance.context()
                elif locust_user_instance.__class__.__name__ == 'APIUser':
                    request_type = "api_action"
                elif locust_user_instance.__class__.__name__ == 'FunctionUser':
                    request_type = "function_action"

                locust_user_instance.environment.events.request.fire(
                    request_type=request_type,
                    name=name,
                    response_time=duration,
                    response_length=0,
                    exception=exception,
                    context=context,
                )

                if exception:
                    print(f"Error Encountered in function: {name} - {exception}")
                    # raise exception # Uncomment if you want the test to stop on error
            return result
        return wrapper
    return decorator