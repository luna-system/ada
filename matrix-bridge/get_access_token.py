#!/usr/bin/env python3
"""
Get Matrix access token for Ada bot account.

Usage:
    uv run matrix-bridge/get_access_token.py

Or with arguments:
    uv run matrix-bridge/get_access_token.py --homeserver https://matrix.org --user ada-ai --save

Or with dependencies in your venv:
    python matrix-bridge/get_access_token.py
"""

import argparse
import json
import sys
from getpass import getpass
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Error: httpx not installed.")
    print()
    print("Install with UV:")
    print("  uv pip install httpx")
    print()
    print("Or with pip:")
    print("  pip install httpx")
    sys.exit(1)


def get_access_token(homeserver: str, user_id: str, password: str, debug: bool = False) -> dict:
    """Login to Matrix and get access token.
    
    Args:
        homeserver: Matrix homeserver URL (e.g., https://matrix.org)
        user_id: Username (without @) or full user ID
        password: Account password
        debug: Show detailed request information
        
    Returns:
        dict with access_token, user_id, device_id
    """
    # Strip @ and homeserver from user_id if provided
    if user_id.startswith("@"):
        user_id = user_id.split(":")[0][1:]  # Strip @ and everything after :
    
    # Ensure homeserver doesn't end with /
    homeserver = homeserver.rstrip("/")
    
    # Try v3 endpoint first, fallback to r0
    login_url = f"{homeserver}/_matrix/client/v3/login"
    
    payload = {
        "type": "m.login.password",
        "identifier": {
            "type": "m.id.user",
            "user": user_id
        },
        "password": password,
        "initial_device_display_name": "Ada Matrix Bridge"
    }
    
    print(f"Logging in to {homeserver} as {user_id}...")
    
    if debug:
        print(f"\nDEBUG: Request URL: {login_url}")
        print(f"DEBUG: Payload (password hidden):")
        debug_payload = payload.copy()
        debug_payload['password'] = "***HIDDEN***"
        print(json.dumps(debug_payload, indent=2))
        print()
    
    try:
        response = httpx.post(
            login_url,
            json=payload,
            timeout=30.0,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        return {
            "access_token": data["access_token"],
            "user_id": data["user_id"],
            "device_id": data.get("device_id", ""),
        }
        
    except httpx.HTTPStatusError as e:
        print(f"\n❌ Login failed: {e.response.status_code}")
        try:
            error_data = e.response.json()
            print(f"Error: {error_data.get('error', 'Unknown error')}")
            if 'errcode' in error_data:
                print(f"Error code: {error_data['errcode']}")
        except:
            print(f"Response: {e.response.text}")
        
        # Try fallback to r0 endpoint with old format
        if "v3" in login_url:
            print("\nℹ️  Trying legacy r0 endpoint with old identifier format...")
            old_login_url = login_url.replace("/v3/", "/r0/")
            old_payload = {
                "type": "m.login.password",
                "user": user_id,
                "password": password,
                "initial_device_display_name": "Ada Matrix Bridge"
            }
            
            try:
                response = httpx.post(
                    old_login_url,
                    json=old_payload,
                    timeout=30.0,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
                print("✅ Legacy endpoint worked!")
                return {
                    "access_token": data["access_token"],
                    "user_id": data["user_id"],
                    "device_id": data.get("device_id", ""),
                }
            except:
                pass
        
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"\n❌ Network error: {e}")
        print(f"Could not connect to {homeserver}")
        sys.exit(1)


def save_to_env(token_data: dict, homeserver: str, env_path: Path):
    """Update .env file with Matrix credentials."""
    
    # Read existing .env or .env.example
    if env_path.exists():
        with open(env_path, "r") as f:
            lines = f.readlines()
    elif env_path.with_name(".env.example").exists():
        print(f"\nℹ️  No .env found, copying from .env.example")
        with open(env_path.with_name(".env.example"), "r") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Update or add Matrix credentials
    updated = {
        "MATRIX_HOMESERVER": homeserver,
        "MATRIX_USER_ID": token_data["user_id"],
        "MATRIX_ACCESS_TOKEN": token_data["access_token"],
    }
    
    new_lines = []
    keys_updated = set()
    
    for line in lines:
        if line.startswith("#") or "=" not in line:
            new_lines.append(line)
            continue
        
        key = line.split("=")[0].strip()
        if key in updated:
            new_lines.append(f"{key}={updated[key]}\n")
            keys_updated.add(key)
        else:
            new_lines.append(line)
    
    # Add any missing keys
    for key, value in updated.items():
        if key not in keys_updated:
            new_lines.append(f"{key}={value}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated {env_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Get Matrix access token for Ada bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Interactive (prompts for all values):
    uv run matrix-bridge/get_access_token.py
    
    # With arguments:
    uv run matrix-bridge/get_access_token.py \\
        --homeserver https://matrix.example.org \\
        --user ada-ai \\
        --save
    
    # Or with activated venv:
    python matrix-bridge/get_access_token.py --save
        """
    )
    
    parser.add_argument(
        "--homeserver",
        help="Matrix homeserver URL (e.g., https://matrix.org)",
        default=None
    )
    parser.add_argument(
        "--user",
        help="Username (without @ or homeserver)",
        default=None
    )
    parser.add_argument(
        "--password",
        help="Password (not recommended, will prompt if not provided)",
        default=None
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save credentials to .env file"
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(__file__).parent / ".env",
        help="Path to .env file (default: ./matrix-bridge/.env)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show detailed request information"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Ada Matrix Bridge - Access Token Generator")
    print("=" * 60)
    print()
    
    # Get homeserver
    homeserver = args.homeserver
    if not homeserver:
        homeserver = input("Homeserver URL (e.g., https://matrix.example.org): ").strip()
    
    if not homeserver.startswith("http"):
        homeserver = f"https://{homeserver}"
    
    # Get username
    user = args.user
    if not user:
        user = input("Username (e.g., ada-ai): ").strip()
    
    if not user:
        print("❌ Username cannot be empty")
        sys.exit(1)
    
    # Get password
    password = args.password
    if not password:
        password = getpass("Password: ")
    
    if not password:
        print("❌ Password cannot be empty")
        sys.exit(1)
    
    print()
    
    # Login and get token
    token_data = get_access_token(homeserver, user, password, debug=args.debug)
    
    print("\n" + "=" * 60)
    print("✅ Login successful!")
    print("=" * 60)
    print()
    print(f"User ID:      {token_data['user_id']}")
    print(f"Device ID:    {token_data['device_id']}")
    print()
    print("Access Token:")
    print("-" * 60)
    print(token_data["access_token"])
    print("-" * 60)
    print()
    
    # Save to .env if requested
    if args.save:
        save_to_env(token_data, homeserver, args.env_file)
        print()
        print(f"🎯 Credentials saved to {args.env_file}")
        print()
        print("Next steps:")
        print("  1. Update other settings in .env (DISPLAY_NAME, etc.)")
        print("  2. Start the bridge: docker compose up -d matrix-bridge")
        print("  3. Invite Ada to a Matrix room!")
    else:
        print("💡 To save to .env automatically, run with --save flag")
        print()
        print("To use this token, add to matrix-bridge/.env:")
        print(f"  MATRIX_HOMESERVER={homeserver}")
        print(f"  MATRIX_USER_ID={token_data['user_id']}")
        print(f"  MATRIX_ACCESS_TOKEN={token_data['access_token']}")
    
    print()


if __name__ == "__main__":
    main()
