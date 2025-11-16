#!/usr/bin/env python3
"""Command line test script for the agent framework."""

import argparse
import os
import sys

from agent import Agent


# Define calculator tools
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract b from a."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Multiply two numbers together."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


# Define the calculator prompt
CALCULATOR_PROMPT = """You are a calculator agent that can compute mathematical expressions.
You can perform addition, subtraction, multiplication, and division.

When given a mathematical expression, break it down into binary operations (operations with two numbers).
Use the available tools to compute each operation step by step.
Follow the standard order of operations (PEMDAS): multiplication and division before addition and subtraction.

Always show your work by breaking down complex expressions into simpler steps.
Return the final numerical result."""


def main():
    """Main entry point for the test script."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Test the agent framework with a calculator agent"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="Name of the model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--base-url",
        default="https://api.openai.com/v1",
        help="OpenAI base URL (default: https://api.openai.com/v1)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "query",
        help="Query to send to the agent"
    )
    
    args = parser.parse_args()
    
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set", file=sys.stderr)
        sys.exit(1)
    
    # Define tools
    tools = [add, subtract, multiply, divide]
    
    # Initialize agent
    agent = Agent(
        prompt=CALCULATOR_PROMPT,
        base_url=args.base_url,
        api_key=api_key,
        model=args.model,
        tools=tools,
        verbose=args.verbose
    )
    
    # Run agent
    response = agent.run(args.query)
    
    # Print response
    print("\nFinal Response:")
    print(response)


if __name__ == "__main__":
    main()
