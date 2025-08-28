import os
import re
import shutil
import sys
import importlib

# === 設定 ===
COMMANDS_DIR = "Commands"
commands = {}
current_dir = os.getcwd()

# === カスタムコマンド読み込み ===
def load_tc_files():
    if not os.path.exists(COMMANDS_DIR):
        os.makedirs(COMMANDS_DIR)
    for filename in os.listdir(COMMANDS_DIR):
        if filename.endswith(".tc"):
            with open(os.path.join(COMMANDS_DIR, filename), "r", encoding="utf-8") as f:
                parse_tc_file(f.read())

def parse_tc_file(content):
    command_match = re.search(r'command\("(.+?)"\)\s*\{([\s\S]+)\}', content)
    if not command_match:
        return
    command_name = command_match.group(1)
    body = command_match.group(2)

    subcommands = {}
    for sub_match in re.finditer(
        r'SubCommand\("(.+?)"\s*,\s*type\((.+?)\)\)\s*\{([\s\S]+?)\}', body):
        sub_name = sub_match.group(1)
        arg_type = sub_match.group(2).strip()
        code_block = sub_match.group(3).strip()
        subcommands[sub_name] = {"code": code_block, "type": arg_type}

    commands[command_name] = subcommands

# === 入力チェック ===
def validate_input(arg, arg_type):
    if arg_type == "Free Description":
        return True
    elif arg_type == "Number":
        return arg.isdigit()
    elif arg_type == "Path":
        return os.path.exists(arg)
    return False

# === 標準コマンド ===
def builtin_command(cmd, args):
    global current_dir
    try:
        if cmd == "cd":
            if len(args) == 0:
                print("Usage: cd <directory>")
            else:
                new_dir = os.path.join(current_dir, args[0])
                os.chdir(new_dir)
                current_dir = os.getcwd()
        elif cmd == "mkdir":
            if len(args) == 0:
                print("Usage: mkdir <directory>")
            else:
                os.makedirs(os.path.join(current_dir, args[0]), exist_ok=True)
        elif cmd == "rd":
            if len(args) == 0:
                print("Usage: rd <directory>")
            else:
                shutil.rmtree(os.path.join(current_dir, args[0]), ignore_errors=True)
        elif cmd == "del":
            if len(args) == 0:
                print("Usage: del <file>")
            else:
                file_path = os.path.join(current_dir, args[0])
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    print("File not found.")
        elif cmd == "copy":
            if len(args) < 2:
                print("Usage: copy <source> <destination>")
            else:
                shutil.copy(os.path.join(current_dir, args[0]),
                            os.path.join(current_dir, args[1]))
        elif cmd == "xcopy":
            if len(args) < 2:
                print("Usage: xcopy <source> <destination>")
            else:
                shutil.copytree(os.path.join(current_dir, args[0]),
                                os.path.join(current_dir, args[1]), dirs_exist_ok=True)
        elif cmd == "help":
            print("Built-in commands: cd, mkdir, rd, del, copy, xcopy, exit, help")
            print("Custom commands loaded: " + ", ".join(commands.keys()))
        elif cmd == "exit":
            print("Exiting...")
            exit()
        else:
            return False
        return True
    except Exception as e:
        print(f"Error: {e}")
        return True

# === メインターミナル ===
def run_terminal():
    while True:
        user_input = input(f"{current_dir}> ").strip()
        if not user_input:
            continue

        parts = user_input.split()
        cmd = parts[0]

        # 標準コマンド優先
        if builtin_command(cmd, parts[1:]):
            continue

        if len(parts) < 2:
            print("Usage: <command> <subcommand> [args]")
            continue

        subcmd = parts[1]
        arg = parts[2] if len(parts) > 2 else ""

        if cmd in commands and subcmd in commands[cmd]:
            sub_info = commands[cmd][subcmd]
            arg_type = sub_info["type"]
            if not validate_input(arg, arg_type):
                print(f"Invalid input type. Expected {arg_type}.")
                continue
            code = sub_info["code"]
            local_vars = {"text": arg, "num": arg}  # text/num どちらも対応
            try:
                exec(code, {}, local_vars)
            except Exception as e:
                print(f"Error executing command: {e}")
        else:
            print("Command or Subcommand not found.")

if __name__ == "__main__":
    load_tc_files()
    print("Custom Terminal started. Type 'help' for commands, 'exit' to quit.")
    run_terminal()
