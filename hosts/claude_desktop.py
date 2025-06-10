import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Optional

from fastmcp.cli import claude
from mcp.cli.claude import get_claude_config_path
from mcp.server.fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


def get_venv_path() -> str:
    """Get the full path to the venv executable."""
    # Check if the Python executable inside the virtual environment is available
    venv_path = Path(os.getenv("VIRTUAL_ENV", "")) / "bin" / "python"
    logger.info(venv_path)
    if not venv_path:
        logger.error(
            "Python executable not found in PATH. Falling back to default Python."
            " Please ensure Python is installed and in your PATH."
        )
        return "python"  # Fall back to default python if not found

    # If the Python executable is found, return its path
    return str(venv_path)


def update_claude_config(
        server_name: str,
        *,
        with_editable: Path | None = None,
        with_packages: list[str] | None = None,
        env_vars: dict[str, str] | None = None,
) -> bool:
    """Add or update a FastMCP server in Claude's configuration.

    Args:
        server_name: Name for the server in Claude's config
        with_editable: Optional directory to install in editable mode
        with_packages: Optional list of additional packages to install
        env_vars: Optional dictionary of environment variables. These are merged with
            any existing variables, with new values taking precedence.

    Raises:
        RuntimeError: If Claude Desktop's config directory is not found, indicating
            Claude Desktop may not be installed or properly set up.
    """
    config_dir = get_claude_config_path()
    venv_path = get_venv_path()

    if not config_dir:
        raise RuntimeError(
            "Claude Desktop config directory not found. Please ensure Claude Desktop"
            " is installed and has been run at least once to initialize its config."
        )

    config_file = config_dir / "claude_desktop_config.json"
    if not config_file.exists():
        try:
            config_file.write_text("{}")
        except Exception as e:
            logger.error(
                "Failed to create Claude config file",
                extra={
                    "error": str(e),
                    "config_file": str(config_file),
                },
            )
            return False

    try:
        config = json.loads(config_file.read_text())
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Always preserve existing env vars and merge with new ones
        if (
                server_name in config["mcpServers"]
                and "env" in config["mcpServers"][server_name]
        ):
            existing_env = config["mcpServers"][server_name]["env"]
            if env_vars:
                # New vars take precedence over existing ones
                env_vars = {**existing_env, **env_vars}
            else:
                env_vars = existing_env

        # Dynamically find the path to main.py
        main_py_path = Path(__file__).parent.parent / "main.py"

        if not main_py_path.exists():
            logger.error("main.py not found in the expected directory.")
            return False

        # Build the command and args for the server
        args = [str(main_py_path)]  # Dynamic path to main.py

        if with_editable:
            args.extend(["--with-editable", str(with_editable)])

        # Collect all packages in a set to deduplicate
        packages = {"fastmcp", "mcp-kakao-map"}
        if with_packages:
            packages.update(pkg for pkg in with_packages if pkg)

        # Add all packages with --with
        for pkg in sorted(packages):
            args.extend(["--with", pkg])

        # Convert file path to absolute before adding to command
        server_config: dict[str, Any] = {"command": venv_path, "args": args}

        # Add environment variables if specified
        if env_vars:
            server_config["env"] = env_vars

        config["mcpServers"][server_name] = server_config

        config_file.write_text(json.dumps(config, indent=2))
        logger.info(
            f"Added server '{server_name}' to Claude config",
            extra={"config_file": str(config_file)},
        )
        return True
    except Exception as e:
        logger.error(
            "Failed to update Claude config",
            extra={
                "error": str(e),
                "config_file": str(config_file),
            },
        )
        return False

def install_to_claude_desktop(
    env_vars: list[str] = None,
):
    """
    Install the MCP to Claude Desktop.
    """
    if not claude.get_claude_config_path():
        sys.exit(1)

    from main import mcp

    name = mcp.name
    server = mcp

    with_packages = getattr(server, "dependencies", []) if server else []

    env_dict: Optional[dict[str, str]] = None
    if env_vars:
        env_dict = {}
        for env_var in env_vars:
            key, value = env_var.split("=", 1)
            env_dict[key.strip()] = value.strip()

    if update_claude_config(
        name,
        with_packages=with_packages,
        env_vars=env_dict,
    ):
        ...
    else:
        sys.exit(1)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description="Install the MCP to Claude Desktop.",
    )
    parser.add_argument(
        "--env",
        "-e",
        action="append",
        help="Environment variables to set for the server.",
    )

    args = parser.parse_args()

    install_to_claude_desktop(
        env_vars=args.env,
    )