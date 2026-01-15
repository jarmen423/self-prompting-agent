import argparse
import sys
import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text

# Import the Agent core
from agent_core import Agent

# Load environment variables
load_dotenv()

def main():
    # 1. Setup Argument Parser
    parser = argparse.ArgumentParser(description="Intent Extraction Agent CLI")
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="The LLM model to use (default: gpt-4o)"
    )
    args = parser.parse_args()

    # 2. Initialize Rich Console
    console = Console()

    # 3. Initialize Agent
    try:
        agent = Agent(model_name=args.model)
    except Exception as e:
        console.print(f"[bold red]Error initializing Agent:[/bold red] {e}")
        sys.exit(1)

    # 4. Initialize History
    history = agent.get_initial_history()

    # Welcome Message
    console.print(Panel.fit(
        f"[bold blue]Intent Extraction Agent[/bold blue]\nModel: [cyan]{args.model}[/cyan]",
        border_style="blue"
    ))
    console.print("[italic]Type 'exit' or 'quit' to stop manually.[/italic]\n")

    # 5. Main Interaction Loop
    try:
        while True:
            # Get User Input
            user_input = console.input("[bold green]You:[/bold green] ").strip()

            if user_input.lower() in ["exit", "quit"]:
                console.print("[yellow]Goodbye![/yellow]")
                break

            if not user_input:
                continue

            # Show a spinner while thinking
            with console.status("[bold green]Thinking...[/bold green]", spinner="dots"):
                response = agent.process_message(history, user_input)

            # Handle Response
            parsed = response.get("parsed", {})
            raw_response = response.get("raw", "")
            saved_to = response.get("saved_to")

            status = parsed.get("status", "error")
            content = parsed.get("content", "")
            thought_process = parsed.get("thought_process", "")

            # Update History
            # We must append the user's input and the assistant's RAW response
            # to keep the conversation valid for the LLM.
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": raw_response})

            # Display Output
            if thought_process:
                console.print(Panel(Text(thought_process, style="dim"), title="Thought Process", border_style="dim"))

            if content and status != "error":
                console.print(Markdown(content))

            # Handle Status
            if status == "executing":
                console.print(f"\n[bold green]Execution Complete![/bold green]")
                if saved_to:
                    console.print(f"Output saved to: [underline]{saved_to}[/underline]")
                else:
                    console.print("No file was saved.")
                break

            elif status == "error":
                console.print(f"[bold red]Error:[/bold red] {content}")

            console.print("") # spacing

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
