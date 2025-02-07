
import inspect
from typing import Literal, Any

from gambax.services import Service, ServiceWrapper
from gambax.utils import load_config, save_config


def register_plugin(plugin, **kwargs):

    config = load_config()

    if isinstance(plugin, ServiceWrapper):
        source_code = inspect.getsource(plugin.__class__)
        logic_func = plugin.function.__code__
        # Insert the source code of the function into the source_code of the ServiceWrapper where its used
        source_code = source_code.replace(f"def {plugin.__class__.__name__}(self, ", f"def {plugin.__class__.__name__}(self, {', '.join(plugin.input_signature)}), ")
        source_code = source_code.replace(f"return self.function(*args, **kwargs)", f"return self.request_impl(*args, **kwargs)")
        source_code = source_code.replace(f"def request_impl(self, ", f"def request_impl(self, {', '.join(plugin.input_signature)}), ")
        source_code = source_code.replace(f"return self.function(*args, **kwargs)", f"return {plugin.function.__name__}(self, *args, **kwargs)")

        with open(f"{plugin.__name__}.py", "w") as f:
            f.write(source_code)

        service_config = {
            "target": f"gambax.plugins.{plugin.__name__}.{plugin.__name__}",
            "params": kwargs.update({"name": plugin.name})
        }
        config['services'].append(service_config)

    elif isinstance(plugin, Service) or plugin.__name__ == "Service":

        source_code = inspect.getsource(plugin)

        with open(f"{plugin.__name__}.py", "w") as f:
            f.write(source_code)

        service_config = {
            "target": f"gambax.plugins.{plugin.__name__}.{plugin.__name__}",
            "params": kwargs
        }
        config['services'].append(service_config)
    else:
        raise ValueError(f"Plugin of type '{plugin.__name__} not supported.")

    save_config(config)
    return True