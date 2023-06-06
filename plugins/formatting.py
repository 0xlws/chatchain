import re


def format_response_md(new_response):
    new_response = f"```md\n{new_response}\n"
    lines_to_write = []
    code_block = False
    for line in new_response.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("```md"):
            lines_to_write.append(f"{stripped_line}\n")
            pass
        elif stripped_line.startswith("```") and not code_block:
            stripped_line = stripped_line.replace("```", "```\n\n```")
            lines_to_write.append(f"{stripped_line}\n")
            code_block = True
        elif stripped_line.endswith("```") and code_block:
            stripped_line += "\n\n```md\n"
            lines_to_write.append(f"{stripped_line}\n")
            code_block = False
        elif code_block:
            lines_to_write.append(f"{line}\n")
        elif stripped_line.startswith("#") or stripped_line == "":
            lines_to_write.append(f"{line}\n")
        else:
            lines_to_write.append(f"{line}\n")

    lines_to_write.append("```")
    return "".join(lines_to_write)


def format_response_py(new_response):
    lines_to_write = []
    code_block = False
    for line in new_response.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("```") and not code_block:
            stripped_line = stripped_line.replace("```", "# ```")
            lines_to_write.append(f"{stripped_line}\n")
            code_block = True
        elif stripped_line.endswith("```") and code_block:
            stripped_line = stripped_line.replace("```", "# ```")
            lines_to_write.append(f"{stripped_line}\n")
            code_block = False
        elif code_block:
            lines_to_write.append(f"{line}\n")
        elif stripped_line.startswith("#") or stripped_line == "":
            lines_to_write.append(f"{line}\n")
        else:
            lines_to_write.append(f"# {line}\n")

    return "".join(lines_to_write)


def format_response_py_v2(new_response):
    if '"""' or "'''" in new_response:
        return format_response_py(new_response)
    lines_to_write = []
    code_block = False
    text_block = False

    for line in new_response.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("```") and not code_block:
            code_block = True
            if text_block:
                if "'''" not in new_response:
                    lines_to_write.append("'''\n")
                elif '"""' not in new_response:
                    lines_to_write.append('"""\n')
                text_block = False
        elif stripped_line.endswith("```") and code_block:
            code_block = False
        elif not code_block:
            if not text_block and stripped_line != "":
                if "'''" not in new_response:
                    lines_to_write.append("'''\n")
                elif '"""' not in new_response:
                    lines_to_write.append('"""\n')
                text_block = True
            if stripped_line.startswith("#") or stripped_line == "":
                lines_to_write.append(f"{line}\n")
            else:
                lines_to_write.append(f"{line}\n")
        else:
            lines_to_write.append(f"{line}\n")

    if text_block:
        if "'''" not in new_response:
            lines_to_write.append("'''\n")
        elif '"""' not in new_response:
            lines_to_write.append('"""\n')

    return "".join(lines_to_write)


def format_assistant_response_py(new_response):
    lines_to_write = ["# Assistant:\n#\n"]
    code_block = False
    for line in new_response.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("```") and not code_block:
            stripped_line = stripped_line.replace("```", "# ```")
            lines_to_write.append(f"{stripped_line}\n")
            code_block = True
        elif stripped_line.endswith("```") and code_block:
            stripped_line = stripped_line.replace("```", "# ```")
            lines_to_write.append(f"{stripped_line}\n")
            code_block = False
        elif code_block:
            lines_to_write.append(f"{line}\n")
        elif stripped_line.startswith("#") or stripped_line == "":
            lines_to_write.append(f"{line}\n")
        else:
            lines_to_write.append(f"# {line}\n")

    return "".join(lines_to_write)


def remove_parentheses_old(text):
    return re.sub(r"\\([^()]*\\)", "", text)


def remove_parentheses(text):
    return re.sub(r"\([^()]*\)", "", text)


def remove_code(text):
    result = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return result if result != text else False


def extract_code(text):
    code_pattern = re.compile(r"```.*?```", re.DOTALL)
    txt = code_pattern.findall(text)
    return "\n\n".join(txt)


def extract_python_code(text):
    code_pattern = re.compile(r"```python.*?```", re.DOTALL)
    txt = code_pattern.findall(text)
    return "\n\n".join(txt)


def remove_backticks(text):
    return text.replace("```", "")
