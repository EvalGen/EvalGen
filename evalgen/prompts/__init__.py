# dynamically create a module variable for each prompt
# list all .jinja files in the current directory
# for each file, create a module variable so that we can import it
# from evalgen.prompts import evaluate as eval_prompt
# eval_prompt.render(response="hello", context="world")

import sys
from collections import namedtuple
from pathlib import Path

from jinja2 import Template

jinja_files = list(Path(__file__).parent.glob("*.jinja"))

# for each file, create a jinja template and store it in a module variable
for jinja_file in jinja_files:
    name = jinja_file.stem
    content = jinja_file.read_text()

    # split out system and user messages
    parts = content.split("END SYSTEM PROMPT")
    system_prompt = parts[0] if len(parts) > 0 else None
    user_prompt = parts[1] if len(parts) > 1 else None

    prompt = namedtuple(name, ["system", "user"])(
        Template(system_prompt) if system_prompt else None,
        Template(user_prompt),
    )
    print(prompt)

    print(f"Creating module variable: {name}")

    setattr(sys.modules[__name__], name, prompt)

# example usage
# from evalgen.prompts import prompt_evaluate as eval_prompt
# eval_prompt.system.render(response="hello", context="world")
# eval_prompt.user.render(response="hello", context="world")
