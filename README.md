<div style="display: flex; align-items: center; justify-content: center; margin: 20px 0;">
  <img 
    src="misc/foreground_gamba.png" 
    alt="Logo"
    style="height: 180px; margin-right: 1rem;"
  />
  <span style="font-size: 8rem; font-weight: bold;">
    Gambax
  </span>
</div>

## ❓ What is Gambax?
Gambax is an easy-to-use development tool for (distributed) LLM applications. It provides several useful features: 
<ul style="list-style: none; margin: 0; padding: 0.1;">
  <li>💥 Local server hosting an API for the LLMs</li>
  <li>💥 Command-line tool to chat with your LLM</li>
  <li>💥 Seamless integration of distributed systems with central LLM</li>
  <li>💥 Easy definition of services for advanced functionalities</li>
  <li>💥 Seamless integration with existing LLM framework</li>
  <li>💥 VS Code extension for inline completion</li>
</ul>

## 🔥 Upcoming 
<ul style="list-style: none; margin: 0; padding: 0.2;">
  <li>[ ] Proper plugin library to directly insert source code and provide models and services to Gambax</li>
  <li>[ ] Extended basic services provided by the API</li>
  <li>[ ] Add streaming API to LLMServer</li>
  <li>[ ] Support of more models especially locally hosted</li>
  <li>[ ] Gradio web interface</li>
  <li>[ ] More stable and refined VS Code inline completions</li>
  <li>[ ] Add LLM Agents for more advanced reasoning</li>
  <li>[ ] Just-in-time server that allows using all tools without launching server previously</li>
  <li>[ ] Improve stability and security of server</li>
</ul>

## 📺 Demo
 - [Command-Line Tool](./examples/command_line.md)
 - [Image Generation](./examples/image_generation.md)
 - [Example Project](./examples/example_project/README.md)

## 📦 Installation

### Prerequisites

- Ensure you have [Node.js](https://nodejs.org/) and [Git](https://git-scm.com/) installed.

### Clone the Repository
```shell
git clone https://github.com/LDenninger/Gambax.git
```

### Install Gambax
```shell
pip install -e .
```

## 🚀 Getting Started

### Setup API
Setup the default OpenAI API with your [OpenAI API key](https://platform.openai.com/api-keys):
```shell
export OPENAI_API_KEY=<OpenAI API key>
```

### Start Gambax Server
```shell
gambax-server
```

### Command-line tool
```shell
gambax Hello, how are you today?
```

### Include Gambax in your App
```python
from gambax import LLMClient
from gambax.utils import message_template

client = LLMClient()

messages = [
    message_template("system", "You are a helpful AI assistant!"),
    message_template("user", "Hey, how are you?"),
]

response = client.request_response(messages)
print(response)
```

## 💻 Command-Line Tool

**Format:** `gambax <question>`

### Special Commands
Special commands have the prefix `\\` a command followed by optional arguments in `{}` brackets.

|  Command | Arguments  | Description  | Example | 
|---|---|---|---|
| insert |  File/Path  | Insert file or all files from path   | `gambax Explain me this file: \\insert{path/to/my/file}` | 
| ag  |  Search pattern  | Insert all files including the pattern | `gambax What does the class MyClass do \\ag{MyClass}`|
| cc  | -  | Continue the last chat  |  `gambax \\cc How is this file different from this file \\insert{path/to/my/file}` |
| exec  | -  | Execute command and load into context  |  `gambax \\exec{python src/test.py} Can you fix the bug?` |

### Custom Commands
To define your own commands simply implement the `Command` base class in `src/interfaces/cli/command.py`:
```python
class MyCommand(Command):
  name: str = "my_awesome_command"
  cmd: str = "mycmd"
  description: str = "My awesome command that dcoes awesome stuff."

  def __init__(self):
    super().__init__(self.name, self.cmd, self.description)

  def command_impl(self, messages: List[Dict[str, str]], position: int) -> List[Dict[str, str]]:
    arguments = self.get_arguments(question[position:])
    ## Implement your logic here ##
    return messages
```

## 🔧 Services
Services provide pre-defined functionalities or specialized API calls that link into the LLM.
They can either explicitly called by hand or implicitely called by the LLM if it implements the `get_tool()` function and the LLM supports function calling.

### Inline Completion 
**Path:** `./services/inline_completion.py` <br/>
**Arguments:** <br/>
 `line (str):` The line to be completed <br/>
 `context_before (str):` Lines before the completion <br/>
 `context_after (str):` Lines after the completion <br/>
 **Returns:** <br/>
 `line_diff (str):` Line completion as differences of the current line

### Image Generation
**Path:** `./services/image_generation.py` <br/>
**Arguments:** <br/>
 `prompt (str):` Prompt used for image generation <br/>
 `size (str):` Size of the image to be generated <br/>
 `quality (str):` Quality of the generated image <br/>
 **Returns:** <br/>
 `url (str):` URL to the image on the OpenAI server

### Custom Services
You can easily define custom services by implementing the `Service` base class in `./services/service.py`.
We use the (OpenAI funciton-calling)[https://platform.openai.com/docs/guides/function-calling] convention
```python
class MyService(Service):
  name: str = "my_service"
  def __init__(self, *args, **kwargs):
    super().__init__(self.name, input_signature=["prompt"], output_signature=["response"])
    return

  def request_impl(self, prompt, *args, **kwargs):
    ## Your logic goes here ##
    return response

    def get_tool(self):
      # Define OpenAI API function call 
      return {}
```



## License
This projects is licensed under the **BSD-3** license.

## Author
Luis Denninger <l_denninger@uni-bonn.de>
