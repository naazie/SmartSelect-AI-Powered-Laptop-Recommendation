import inspect
from typing import Type, Any

def apply_measurement_to_async_methods(myClass: Type, measure_decorator_factory: Any):
    _globals_copy = myClass.__dict__.copy()

    for name, obj in _globals_copy.items():
        if inspect.isfunction(obj) and inspect.iscoroutinefunction(obj) and not name.startswith('__'):
            _metric_name = name.replace('_', ' ').capitalize()
            wrapped_method = measure_decorator_factory(_metric_name)(obj)
            setattr(myClass, name, wrapped_method)