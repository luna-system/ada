#!/usr/bin/env python3
"""
Ada Master CLI - Unified interface for all Ada operations.

Supports both local (no Docker) and Docker modes, with smart auto-detection.
"""
import click
import sys
import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def info(msg: str):
    """Print info message."""
    click.echo(f"{BLUE}ℹ{RESET} {msg}")


def success(msg: str):
    """Print success message."""
    click.echo(f"{GREEN}✓{RESET} {msg}")


def warning(msg: str):
    """Print warning message."""
    click.echo(f"{YELLOW}⚠{RESET} {msg}")


def error(msg: str):
    """Print error message."""
    click.echo(f"{RED}✗{RESET} {msg}", err=True)


def check_command(cmd: str) -> bool:
    """Check if a command exists."""
    return shutil.which(cmd) is not None


def check_service(host: str, port: int, name: str) -> bool:
    """Check if a service is accessible."""
    import socket
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def detect_environment() -> Tuple[bool, bool, bool]:
    """
    Detect what's available.
    
    Returns:
        (has_docker, has_ollama, has_chromadb)
    """
    has_docker = check_command("docker")
    has_ollama = check_service("localhost", 11434, "Ollama")
    has_chromadb = check_service("localhost", 8000, "ChromaDB")
    
    return has_docker, has_ollama, has_chromadb


@click.group()
@click.version_option(version="2.2.0")
def cli():
    """Ada - Your local AI assistant (Docker optional!)"""
    pass


@cli.command()
def doctor():
    """Check system health and prerequisites."""
    click.echo(f"\n{BOLD}Ada Health Check{RESET}\n")
    
    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_ok = sys.version_info >= (3, 13)
    
    if python_ok:
        success(f"Python {py_version}")
    else:
        error(f"Python {py_version} (need >= 3.13)")
        
        # Check if Nix is available as a solution
        if check_command("nix"):
            click.echo(f"\n  {BLUE}💡 Solution:{RESET} Use Nix for Python 3.13:")
            click.echo(f"     {BOLD}nix develop{RESET}")
            click.echo(f"     or with direnv: {BOLD}direnv allow{RESET}\n")
        else:
            click.echo(f"\n  {BLUE}💡 Solutions:{RESET}")
            click.echo(f"     1. Install Nix: https://nixos.org/download")
            click.echo(f"        Then run: {BOLD}nix develop{RESET}")
            click.echo(f"     2. Use Docker: {BOLD}ada run --docker{RESET}")
            click.echo(f"     3. Build Python 3.13 from source\n")
    
    # Check environment
    has_docker, has_ollama, has_chromadb = detect_environment()
    
    if has_docker:
        success("Docker available")
    else:
        warning("Docker not found (optional)")
    
    if has_ollama:
        success("Ollama running (localhost:11434)")
    else:
        warning("Ollama not running (required for LLM)")
    
    if has_chromadb:
        success("ChromaDB running (localhost:8000)")
    else:
        info("ChromaDB not running (will use embedded mode)")
    
    # Check virtual environment
    if os.getenv("VIRTUAL_ENV"):
        success(f"Virtual environment: {os.getenv('VIRTUAL_ENV')}")
    else:
        warning("Not in virtual environment (recommended)")
    
    # Check .env file
    if Path(".env").exists():
        success(".env file found")
    else:
        warning(".env file missing (will use defaults)")
    
    # Check data directory
    if Path("data").exists():
        success("data/ directory exists")
    else:
        info("data/ directory will be created")
    
    click.echo()


@cli.command()
@click.option("--docker", is_flag=True, help="Force Docker mode")
@click.option("--local", is_flag=True, help="Force local mode (no Docker)")
@click.option("--dev", is_flag=True, help="Development mode (hot reload)")
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=7000, help="Port to bind to")
def run(docker: bool, local: bool, dev: bool, host: str, port: int):
    """Start Ada (auto-detects best mode)."""
    
    if docker and local:
        error("Cannot use both --docker and --local")
        sys.exit(1)
    
    # Auto-detect if no mode specified
    if not docker and not local:
        has_docker, has_ollama, _ = detect_environment()
        
        if has_ollama:
            local = True
            info("Local Ollama detected → using local mode")
        elif has_docker:
            docker = True
            info("Docker available, no local Ollama → using Docker mode")
        else:
            error("No Ollama or Docker found. Install one of:")
            click.echo("  • Ollama: https://ollama.ai")
            click.echo("  • Docker: https://docker.com")
            sys.exit(1)
    
    if docker:
        click.echo(f"\n{BOLD}Starting Ada (Docker mode){RESET}\n")
        cmd = ["docker", "compose", "up"]
        if not dev:
            cmd.append("-d")
        subprocess.run(cmd)
        
        if not dev:
            success("Ada started in background")
            info("View logs: docker compose logs -f brain")
            info("Stop: docker compose down")
    
    elif local:
        click.echo(f"\n{BOLD}Starting Ada (Local mode){RESET}\n")
        
        # Check Ollama
        if not check_service("localhost", 11434, "Ollama"):
            error("Ollama not running! Start it first:")
            click.echo("  ollama serve")
            sys.exit(1)
        
        # Set environment variables
        os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")
        os.environ.setdefault("CHROMA_MODE", "embedded")
        os.environ.setdefault("DATA_DIR", "./data")
        
        success("Using local Ollama")
        info("Using embedded ChromaDB")
        
        # Run uvicorn
        if dev:
            cmd = ["uvicorn", "brain.app:app", "--host", host, "--port", str(port), "--reload"]
        else:
            cmd = ["uvicorn", "brain.app:app", "--host", host, "--port", str(port)]
        
        info(f"Starting brain on {host}:{port}...")
        subprocess.run(cmd)


@cli.command()
def status():
    """Show Ada service status."""
    click.echo(f"\n{BOLD}Ada Status{RESET}\n")
    
    has_docker, has_ollama, has_chromadb = detect_environment()
    
    # Check brain
    if check_service("localhost", 8000, "Brain"):
        success("Brain API running (http://localhost:8000)")
    else:
        info("Brain API not running")
    
    # Check Ollama
    if has_ollama:
        success("Ollama running (http://localhost:11434)")
    else:
        warning("Ollama not running")
    
    # Check ChromaDB
    if has_chromadb:
        success("ChromaDB running (http://localhost:8000)")
    else:
        info("ChromaDB not running (embedded mode active)")
    
    # Check Docker containers if available
    if has_docker:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            click.echo(f"\n{BOLD}Docker Containers:{RESET}")
            subprocess.run(["docker", "compose", "ps"])
    
    click.echo()


@cli.command()
def stop():
    """Stop all Ada services."""
    has_docker, _, _ = detect_environment()
    
    if has_docker:
        subprocess.run(["docker", "compose", "down"])
        success("Docker services stopped")
    else:
        info("No Docker services running")
    
    # Kill local process if running
    result = subprocess.run(
        ["pgrep", "-f", "uvicorn brain.app:app"],
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        pid = result.stdout.strip().split()[0]
        subprocess.run(["kill", pid])
        success(f"Stopped local brain (PID {pid})")


@cli.command()
@click.argument("message")
def chat(message: str):
    """Quick one-shot chat with Ada."""
    # Try to use ada-cli if installed
    if check_command("ada-cli"):
        subprocess.run(["ada-cli", message])
    else:
        # Fall back to direct API call
        import requests
        try:
            response = requests.post(
                "http://localhost:8000/v1/chat/stream",
                json={"prompt": message},
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    print(line.decode())
        except requests.exceptions.RequestException as e:
            error(f"Failed to connect to Ada: {e}")
            info("Is Ada running? Try: ada run")
            sys.exit(1)


@cli.command()
@click.argument("service", required=False)
@click.option("-f", "--follow", is_flag=True, help="Follow log output")
def logs(service: Optional[str], follow: bool):
    """View service logs."""
    cmd = ["docker", "compose", "logs"]
    if follow:
        cmd.append("-f")
    if service:
        cmd.append(service)
    
    subprocess.run(cmd)


@cli.command()
@click.option("--error", "-e", help="Paste error message directly")
@click.option("--file", "-f", type=click.Path(exists=True), help="Read error from file")
@click.option("--last", is_flag=True, help="Analyze last command output")
def rescue(error: Optional[str], file: Optional[str], last: bool):
    """🚑 Code ambulance - Emergency debugging help (on-device!)
    
    Drop in when your code is broken. Ada will diagnose and suggest fixes.
    Works on ANY codebase - no prior knowledge needed.
    
    Examples:
      ada rescue                           # Interactive mode
      ada rescue -e "KeyError: 'lines'"    # Quick diagnosis
      ada rescue -f error.log              # Analyze error file
      ada rescue --last                    # Check last command
    """
    click.echo(f"\n{BOLD}🚑 Ada Code Ambulance{RESET}\n")
    click.echo("On-device emergency code help\n")
    
    # Get error message from various sources
    error_text = None
    context_info = ""
    
    if error:
        error_text = error
        context_info = "Direct input"
    elif file:
        error_text = Path(file).read_text()
        context_info = f"From {file}"
    elif last:
        # Try to get last command output from shell history
        try:
            result = subprocess.run(
                ["bash", "-c", "fc -ln -1"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                error_text = result.stdout
                context_info = "Last command"
            else:
                warning("Could not read last command")
        except Exception:
            warning("Could not read shell history")
    
    if not error_text:
        # Interactive mode
        click.echo("What happened? Paste your error message:")
        click.echo("(Press Ctrl+D when done, or Ctrl+C to cancel)\n")
        
        try:
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            error_text = "\n".join(lines)
            context_info = "Interactive input"
        except KeyboardInterrupt:
            click.echo("\n\nCancelled.")
            return
    
    if not error_text or not error_text.strip():
        error("No error message provided")
        return
    
    info(f"Analyzing error ({context_info})...")
    click.echo()
    
    # Quick pattern-based diagnosis
    error_lower = error_text.lower()
    
    diagnoses = []
    
    # Pattern matching for common issues
    if "keyerror" in error_lower:
        diagnoses.append({
            "pattern": "Dictionary KeyError",
            "confidence": 0.9,
            "fix": "Key doesn't exist in dictionary. Use .get() or check with 'if key in dict'",
            "example": "result.metadata.get('key', 'default')"
        })
    
    if "modulenotfounderror" in error_lower or "no module named" in error_lower:
        diagnoses.append({
            "pattern": "Import/Module Error",
            "confidence": 0.85,
            "fix": "Module not found. Check: 1) Module installed? 2) PYTHONPATH set? 3) Import path correct?",
            "example": "pip install <module> or check sys.path"
        })
    
    if ("typeerror" in error_lower and "nonetype" in error_lower) or "attributeerror" in error_lower:
        diagnoses.append({
            "pattern": "Unexpected None Value",
            "confidence": 0.8,
            "fix": "Variable is None. Add None check before using",
            "example": "if obj is not None: obj.method()"
        })
    
    if "indentationerror" in error_lower:
        diagnoses.append({
            "pattern": "Python Indentation",
            "confidence": 0.95,
            "fix": "Inconsistent indentation. Use 4 spaces per level",
            "example": "Run: autopep8 --in-place --select=E1 <file>"
        })
    
    if "await" in error_lower and ("was never awaited" in error_lower or "coroutine" in error_lower):
        diagnoses.append({
            "pattern": "Missing await",
            "confidence": 0.9,
            "fix": "Async function not awaited. Add 'await' keyword",
            "example": "result = await async_function()"
        })
    
    if diagnoses:
        click.echo(f"{GREEN}💡 Diagnosis:{RESET}\n")
        
        for i, diag in enumerate(diagnoses, 1):
            click.echo(f"{BOLD}{i}. {diag['pattern']}{RESET}")
            click.echo(f"   Confidence: {int(diag['confidence']*100)}%")
            click.echo(f"   {BLUE}Fix:{RESET} {diag['fix']}")
            if 'example' in diag:
                click.echo(f"   {YELLOW}Example:{RESET} {diag['example']}")
            click.echo()
        
        click.echo(f"{GREEN}✓ Analysis complete{RESET}")
        click.echo(f"\n{BLUE}💭 Pro tip:{RESET} These patterns work on ANY codebase, on-device!")
        click.echo("   No internet needed. Just local pattern matching.\n")
    else:
        click.echo(f"{YELLOW}⚠️  No matching patterns found{RESET}")
        click.echo("\nError message (first 500 chars):")
        click.echo(error_text[:500])
        click.echo("\n💡 Tips for debugging:")
        click.echo("   1. Read the error carefully - it tells you what went wrong")
        click.echo("   2. Check the file and line number mentioned")
        click.echo("   3. Search for the error type online")
        click.echo("   4. Ask Ada in chat mode: ada chat 'explain this error'")
        click.echo()


@cli.command()
@click.option("--focus", type=click.Choice(["general", "architecture", "features", "testing", "docs"]),
              default="general", help="What to focus on")
def introspect(focus: str):
    """🔮 Ada reads herself and suggests next steps
    
    Self-awareness mode - Ada analyzes her own state and recommends priorities.
    Great for: "What should I work on next?" or understanding the codebase.
    
    Examples:
      ada introspect                    # General overview
      ada introspect --focus architecture  # Architecture review
      ada introspect --focus testing    # Test coverage analysis
    """
    click.echo(f"\n{BOLD}🔮 Ada Introspection{RESET}\n")
    
    # Check if we're in Ada's workspace
    if not Path(".ai").exists():
        warning("Not in Ada's workspace (.ai/ directory not found)")
        click.echo("\nThis command works best in Ada's codebase.")
        click.echo("But the principle works anywhere: structure your docs as .ai/ and Ada can read them!")
        return
    
    info(f"Focus: {focus}")
    info("Reading .ai/ documentation...")
    click.echo()
    
    # Import the introspection tool
    try:
        sys.path.insert(0, str(Path(__file__).parent / "ada-mcp" / "src"))
        from ada_mcp.tools.introspection import ada_introspect
        import asyncio
        
        result = asyncio.run(ada_introspect(
            focus=focus,
            workspace_root=str(Path.cwd())
        ))
        
        if result.success:
            click.echo(result.content)
            click.echo(f"\n{GREEN}✓ Introspection complete{RESET}")
            click.echo(f"\n{BLUE}💭 Pro tip:{RESET} Ada just read her own docs and analyzed herself.")
            click.echo("   This is pure Python file reading - works on any structured docs!")
        else:
            error(f"Introspection failed: {result.content}")
    
    except ImportError as e:
        error(f"Could not load introspection tool: {e}")
        info("Make sure ada-mcp is installed: pip install -e ada-mcp/")
    except Exception as e:
        error(f"Introspection error: {e}")


@cli.command()
def setup():
    """Initial setup wizard."""
    click.echo(f"\n{BOLD}Ada Setup Wizard{RESET}\n")
    
    # Check prerequisites
    if not sys.version_info >= (3, 13):
        error("Python 3.13+ required")
        sys.exit(1)
    
    success("Python version OK")
    
    # Create virtual environment if needed
    if not Path(".venv").exists():
        info("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"])
        success("Virtual environment created")
    else:
        success("Virtual environment exists")
    
    # Install dependencies
    if click.confirm("Install/update dependencies?", default=True):
        venv_python = ".venv/bin/python"
        if check_command("uv"):
            subprocess.run(["uv", "pip", "install", "-e", "."])
        else:
            subprocess.run([venv_python, "-m", "pip", "install", "-e", "."])
        success("Dependencies installed")
    
    # Create .env if missing
    if not Path(".env").exists():
        if click.confirm("Create .env file from template?", default=True):
            if Path(".env.example").exists():
                shutil.copy(".env.example", ".env")
                success(".env file created")
                info("Edit .env to customize configuration")
            else:
                warning(".env.example not found")
    else:
        success(".env file exists")
    
    # Create data directory
    Path("data").mkdir(exist_ok=True)
    success("data/ directory ready")
    
    click.echo(f"\n{GREEN}{BOLD}Setup complete!{RESET}")
    click.echo("\nNext steps:")
    click.echo("  1. Edit .env if needed")
    click.echo("  2. Install Ollama: https://ollama.ai")
    click.echo("  3. Pull a model: ollama pull deepseek-r1:14b")
    click.echo("  4. Start Ada: ada run")
    click.echo()


if __name__ == "__main__":
    cli()
