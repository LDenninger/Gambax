# Command-Line Tool
For the command-line tool first launch the gambax server with `gambax-server`

## Question Answering

```shell
❯ gambax Write me a script that output the fibonacci numbers

  User:
  Write me a script that output the fibonacci numbers
  Assistant:[t: 2.041s] 
  def fibonacci(n):
      a, b = 0, 1
      for _ in range(n):
          print(a, end=' ')
          a, b = b, a + b
  
  # Change the value of n to output more or fewer Fibonacci numbers
  n = 10
  fibonacci(n)
```

## Follow-Up Questions
```shell
❯ gambax \\cc Change it to a script that uses argparse to parse the appropriate arguments

  User:
  \cc Change it to a script that uses argparse to parse the appropriate arguments
  Assistant:[t: 2.590s] 
  import argparse
  
  def fibonacci(n):
      a, b = 0, 1
      for _ in range(n):
          print(a, end=' ')
          a, b = b, a + b
      print()  # for a new line after the output
  
  if __name__ == "__main__":
      parser = argparse.ArgumentParser(description="Generate Fibonacci numbers.")
      parser.add_argument("count", type=int, help="Number of Fibonacci numbers to generate")
      
      args = parser.parse_args()
      fibonacci(args.count)

```

## Insert Files
```shell
❯ gambax \\insert{README.md} What is the project for
  
  User:
  \insert{README.md} What is the project for
  Assistant:[t: 1.964s] 
  Gambax is a development tool designed for creating applications that utilize large language models (LLMs).
  It offers features such as local server hosting for LLM APIs, a command-line interface for interacting with LLMs,
  a VS Code extension for inline code completion, and integration capabilities for distributed systems.
  The tool aims to simplify the development process for LLM applications by providing easy service definitions and advanced functionalities.

```

## Debug files
**File:**
```python
def fibonacci(self, n):
    fib_sequence = [0, 1]
    while len(fib_sequence) < n:
        next_fib = fib_sequence[-1] + fib_sequence[-3]
        fib_sequence.add(next_fib)
    return fib_sequence

# Compute Fibonacci numbers up to 20
fibonacci_numbers = fibonacci(20)
print f"{fibonacci_numbers}" 
```
```shell
❯ gambax \\exec{"python test.py"} Fix the script
  
  User:
  \exec{python test.py} Fix the script
  Assistant:[t: 2.382s] 
  def fibonacci(n):
      fib_sequence = [0, 1]
      while len(fib_sequence) < n:
          next_fib = fib_sequence[-1] + fib_sequence[-2]
          fib_sequence.append(next_fib)
      return fib_sequence
  
  # Compute Fibonacci numbers up to 20
  fibonacci_numbers = fibonacci(20)
  print(fibonacci_numbers)

```

## Generate Images
```shell
❯ gambax Generate a wide image of the New York Skyline

    User:
    Generate a wide image of the New York Skyline
    Assistant:[t: 24.939s] 
    https://oaidalleapiprodscus.blob.core.windows.net/private/org-kQhNtYCMVW3De81Z7CnmI93x/user-h6qXZR5zPCky6liNEDsokGa9/img-xkBcRbB51LGlV1ElrrXFVjdx.png?st=2025-02-07T13%3A18%3A48Z&se=2025-02-07T15%3A18%3A48Z&sp=r&sv=2024-08-04&sr=b&rscd=inline&rsct=image/png&skoid=d505667d-d6c1-4a0a-bac7-5c84a87759f8&sktid=a48cca56-e6da-484e-a814-9c849652bcb3&skt=2025-02-07T01%3A11%3A51Z&ske=2025-02-08T01%3A11%3A51Z&sks=b&skv=2024-08-04&sig=P/CPFumnpIGYxhaJXY4SdmEK/pCcBDmWpBN3i5yTobw%3D

```
<div style="text-align: center;">
    <img src="../misc/gen_examples/ny_skyline.png" alt="Description of Image" />
</div>
