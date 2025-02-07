from typing import Optional, List, Dict, Any
import threading
import inspect
from abc import abstractmethod

class Service:

    def __init__(self,
                  name: str,
                  input_signature: List[str] = [],
                  output_signature: List[str] = [],
                  description: str = ""
                  ):
        
        self.name = name
        self.input_signature = input_signature
        self.output_signature = output_signature
        self.description = description

        self._callback_function = None
        self._worker_thread = None
        self._worker_finished = False

    def __call__(self, *args, **kwargs):
        return self.request(*args, **kwargs)

    def request(self, callback_func: Optional[callable]=None, *args, **kwargs):
        if callback_func is not None:
            self._callback_function = callback_func
            self._start_worker_thread()
        else:
            return self.request_impl(*args, **kwargs)

    @abstractmethod
    def request_impl(self, *args, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError("Services must implement request_impl() method")

    def _start_worker_thread(self, *args, **kwargs):
        def _run_async_worker():
            response = self.request_impl(*args, **kwargs)
            self._callback_function(**response)
            self._worker_finished = True
        if self._worker_thread is not None:
            if self._worker_finished:
                self._worker_thread.join()
                self._worker_thread = None
            else:
                return False

        if self._worker_thread is None or not self._worker_thread.is_alive():
            self._worker_finished = False
            self._worker_thread = threading.Thread(target=_run_async_worker)
            self._worker_thread.start()

    @abstractmethod
    def get_tool(self) -> str:
        """
            Get the tool definition as a dictionary.
            We follow the convention of the OpenAI API: https://platform.openai.com/docs/guides/function-calling
        """
        return None

    def __str__(self):
        return f"Service '{self.name}': {' '.join(self.input_signature)} -> {' '.join(self.output_signature)}"
    

class ServiceWrapper(Service):

    def __init__(self, function: callable, name: str = None, input_signature: List[str] = None, output_signature: List[str] = [], description: str = ""):
        name = name or function.__name__
        sig = inspect.signature(function)
        input_signature = list(sig.parameters.keys())

        super().__init__(name, input_signature, output_signature, description)

        self.function = function

    def request_impl(self, *args, **kwargs) -> Dict[str, Any]:
        return self.function(*args, **kwargs)

