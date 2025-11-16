# Agent framework vibe coding prompt

## Initial prompt
Create a simple generative agent framework for me in Python. The requirements are:
- For testing, use the python virtual environment already installed at ./venv. DO NOT create another
  virtual environment. This one already has the pydantic and openai packages installed.
- The code for the agent should live in a single python file: `agent.py`
- Use the OpenAI client sdk to talk to LLMs.
- The main class is called `Agent`. It has a constructor that takes a prompt, an OpenAI base URL,
  an OpenAI token, a model name, a list of tools, and a boolean parameter `verbose`, which defaults to False.
- Tools are python functions with type annotations and a docstring describing the function.
- Use the pydantic library to convert function signatures to JSON schema used to describe each tool to OpenAI
- If `verbose` is True, pretty print details about the messages sent back and forth to the LLM.

## Follow up prompt for test script
Now, make a separate command line script `agent_test.py` that uses argparse to parse command line arguments,
initializes an agent, runs it, and prints the response. The requirements are:

- `agent_test.py` should take as command line arguments:
  --model NAME
    name of the model, defaults to gpt-4o
  --base-url URL
    OpenAI base url, defaults to https://api.openai.com/v1
  --verbose
    If specified, set verbose on the agent.
  QUERY
    Positional command line argument for the query to be sent to the agent (required)
- `agent_test.py` should take the api key from the environment variable `OPENAI_API_KEY` and throw an
   error if it is not set
- `agent_test.py` should define a prompt that the agent is a calculator. It can compute expressions involving
  addition, subtraction, multiplication, and division. It should break the full expression into binary operations,
  which are computed using the tools.
- `agent_test.py` should pass the agent four tools: `add`, `subtract`, `multiply`, and `divide`. Each tool has
  two numeric parameters and returns a number.
