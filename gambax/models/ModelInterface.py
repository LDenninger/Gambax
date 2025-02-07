from typing import List, Optional
from abc import abstractmethod
import threading

class ModelInterface:
    """
        The model interface to be implemented by all LLM models
        to be used with the LLM server.
    """

    def __init__(self, name: str):
        self.name = name


    def __call__(self, messages: List[str], callback: Optional[callable] = None, *args, **kwargs):

        if callback is not None:
            self._async_wrapper(callback, messages=messages, *args, **kwargs)
            return True

        response = self.call_impl(messages, *args, **kwargs)
        return response
    
    def _async_wrapper(self, callback: callable, *args, **kwargs):

        def __thread_func():
            response = self.call_impl(*args, **kwargs)
            try:
                callback(response)
            except Exception as e:
                print(f"Error in callback: {str(e)}")
        
        thread = threading.Thread(target=__thread_func)
        thread.start()
    
    @abstractmethod
    def call_impl(self, messages: List[str], *args, **kwargs) -> str:
        raise NotImplementedError("'call_impl()' must be defined by implemented models.")
    
    def __str__(self):
        return self.name
    
class ModelWrapper(ModelInterface):

    def __init__(self, name: str):
        super().__init__(name)
        self._async = threading.Lock()