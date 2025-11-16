"""Simple generative agent framework using OpenAI API."""

import inspect
import json
from typing import Any, Callable, Dict, List, Optional, get_type_hints

from openai import OpenAI
from pydantic import TypeAdapter, create_model
from pydantic.fields import FieldInfo


class Agent:
    """A generative agent that can use tools to accomplish tasks."""
    
    def __init__(
        self,
        prompt: str,
        base_url: str,
        api_key: str,
        model: str,
        tools: List[Callable],
        verbose: bool = False
    ):
        """Initialize the agent.
        
        Args:
            prompt: System prompt for the agent
            base_url: OpenAI API base URL
            api_key: OpenAI API key
            model: Model name to use
            tools: List of tool functions
            verbose: Whether to print detailed messages
        """
        self.prompt = prompt
        self.model = model
        self.verbose = verbose
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        
        # Convert tools to OpenAI format
        self.tools = tools
        self.tool_map = {tool.__name__: tool for tool in tools}
        self.tool_schemas = [self._function_to_schema(tool) for tool in tools]
    
    def _function_to_schema(self, func: Callable) -> Dict[str, Any]:
        """Convert a Python function to OpenAI tool schema using pydantic.
        
        Args:
            func: The function to convert
            
        Returns:
            OpenAI tool schema dictionary
        """
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        # Build pydantic fields
        fields = {}
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, Any)
            
            # Get parameter description from docstring if available
            description = f"Parameter {param_name}"
            
            # Create field with type and description
            if param.default == inspect.Parameter.empty:
                fields[param_name] = (param_type, FieldInfo(description=description))
            else:
                fields[param_name] = (param_type, FieldInfo(default=param.default, description=description))
        
        # Create a pydantic model dynamically
        model = create_model(f"{func.__name__}_params", **fields)
        
        # Get JSON schema from pydantic model
        schema = model.model_json_schema()
        
        # Build OpenAI tool schema
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or f"Function {func.__name__}",
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", []),
                    "additionalProperties": False
                }
            }
        }
    
    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool function with the given arguments.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Result of the tool call
        """
        if tool_name not in self.tool_map:
            raise ValueError(f"Tool {tool_name} not found")
        
        tool = self.tool_map[tool_name]
        return tool(**arguments)
    
    def run(self, user_message: str, max_iterations: int = 10) -> str:
        """Run the agent with a user message.
        
        Args:
            user_message: The user's input message
            max_iterations: Maximum number of iterations to run
            
        Returns:
            The final response from the agent
        """
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_message}
        ]
        
        for iteration in range(max_iterations):
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"Iteration {iteration + 1}")
                print(f"{'='*60}")
                print(f"\nMessages sent to LLM:")
                print(json.dumps(messages, indent=2))
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas if self.tool_schemas else None
            )
            
            message = response.choices[0].message
            
            if self.verbose:
                print(f"\nResponse from LLM:")
                print(f"Role: {message.role}")
                print(f"Content: {message.content}")
                if message.tool_calls:
                    print(f"Tool calls: {len(message.tool_calls)}")
                    for tool_call in message.tool_calls:
                        print(f"  - {tool_call.function.name}({tool_call.function.arguments})")
            
            # Add assistant message to history
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (message.tool_calls or [])
                ] if message.tool_calls else None
            })
            
            # If no tool calls, we're done
            if not message.tool_calls:
                return message.content or ""
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if self.verbose:
                    print(f"\nCalling tool: {tool_name}")
                    print(f"Arguments: {json.dumps(arguments, indent=2)}")
                
                try:
                    result = self._call_tool(tool_name, arguments)
                    if self.verbose:
                        print(f"Result: {result}")
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                except Exception as e:
                    if self.verbose:
                        print(f"Error: {e}")
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": str(e)})
                    })
        
        # If we hit max iterations, return what we have
        return "Maximum iterations reached without final answer."
