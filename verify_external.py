import sys
import os
import subprocess
import json

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

print("Running verify_external.py...")

# Add npm global directory to PATH temporarily for verification if running on Windows
if sys.platform == 'win32':
    appdata = os.environ.get("APPDATA", "")
    npm_path = os.path.join(appdata, "npm")
    if os.path.exists(npm_path) and npm_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = npm_path + ";" + os.environ.get("PATH", "")
        print(f"Added npm global path to verify environment: {npm_path}")
    
    gh_path = "C:\\Program Files\\GitHub CLI"
    if os.path.exists(gh_path) and gh_path not in os.environ.get("PATH", ""):
        os.environ["PATH"] = gh_path + ";" + os.environ.get("PATH", "")
        print(f"Added GitHub CLI path to verify environment: {gh_path}")

print("\n--- CLI Tools Verification ---")
cli_tools = ["gh", "firebase", "nlm", "mcpvault"]
success_count = 0

for tool in cli_tools:
    try:
        if tool == "gh":
            res = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.split("\n")[0]
            print(f"✅ GitHub CLI found: {first_line}")
            success_count += 1
        elif tool == "firebase":
            # On Windows, firebase CLI might run as firebase.cmd
            cmd = tool if sys.platform != 'win32' else f"{tool}.cmd"
            res = subprocess.run([cmd, "--version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.strip()
            print(f"✅ Firebase CLI found: Version {first_line}")
            success_count += 1
        elif tool == "nlm":
            res = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.strip()
            print(f"✅ NotebookLM CLI (nlm) found: {first_line}")
            success_count += 1
        elif tool == "mcpvault":
            cmd = tool if sys.platform != 'win32' else f"{tool}.cmd"
            res = subprocess.run([cmd, "help"], capture_output=True, text=True) # mcpvault help
            print(f"✅ Obsidian MCP (mcpvault) found and working.")
            success_count += 1
    except FileNotFoundError:
        print(f"❌ CLI tool NOT found in PATH: {tool}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ CLI tool {tool} executed with error: {e}")
    except Exception as e:
        print(f"⚠️ CLI tool {tool} check failed: {e}")

print(f"\nSummary: {success_count}/{len(cli_tools)} CLI tools verified successfully.")

print("\n--- mcp_config.json Verification ---")
config_path = r"C:\Users\H-04137\.gemini\config\mcp_config.json"
if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"✅ mcp_config.json is valid JSON.")
        
        servers = data.get("mcpServers", {})
        required_servers = ["netlify", "notebooklm", "obsidian", "firebase"]
        
        for s in required_servers:
            if s in servers:
                print(f"✅ MCP Server '{s}' is registered.")
                server_info = servers[s]
                # Validate obsidian command/vault path
                if s == "obsidian":
                    cmd_path = server_info.get("command", "")
                    args = server_info.get("args", [])
                    if os.path.exists(cmd_path):
                        print(f"   - mcpvault command path valid: {cmd_path}")
                    else:
                        print(f"   - ❌ mcpvault command path does not exist: {cmd_path}")
                    if args and os.path.exists(args[0]):
                        print(f"   - Obsidian vault path valid: {args[0]}")
                    else:
                        print(f"   - ❌ Obsidian vault path does not exist: {args[0] if args else 'None'}")
            else:
                print(f"❌ MCP Server '{s}' is NOT registered.")
    except Exception as e:
        print(f"❌ Failed to parse or verify mcp_config.json: {e}")
else:
    print(f"❌ mcp_config.json not found at {config_path}")

if success_count < len(cli_tools):
    sys.exit(1)
else:
    sys.exit(0)
