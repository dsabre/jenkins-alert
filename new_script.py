import os

def prompt_string(prompt: str, required: bool = False):
    response = input(prompt)

    if required:
        while not response:
            print("Please enter a value.")
            response = prompt_string(prompt, required)

    return response


def prompt_float(prompt: str, default: float = 0.0):
    response = input(prompt)

    if not response:
        return default

    try:
        return float(response)
    except ValueError:
        print(f"Could not convert '{response}' to a float.")
        return prompt_float(prompt, default)


def prompt_int(prompt: str, choices: list = [], default: int = 0):
    response = input(prompt)

    if not response:
        return default

    try:
        response = int(response)
    except ValueError:
        print(f"Could not convert '{response}' to a int.")
        return prompt_int(prompt, choices, default)

    if choices and response not in choices:
        print(f"Please enter a valid choice from the following: {choices}")
        return prompt_int(prompt, choices, default)

    return response


def write_file(filename: str, contents: str, path: str = "."):
    with open('/'.join([path, filename]), "w") as f:
        f.write(contents)


JENKINS_PROJECT = prompt_string("JENKINS_PROJECT: ", required=True)
JENKINS_EXTRA_JOBS = prompt_string("JENKINS_EXTRA_JOBS: ", required=True)
JENKINS_URL = prompt_string("JENKINS_URL: ", required=True)
JENKINS_USERNAME = prompt_string("JENKINS_USERNAME: ", required=True)
JENKINS_PASSWORD = prompt_string("JENKINS_PASSWORD: ", required=True)
STOP_ON_NOT_RUNNING = prompt_int("STOP_ON_NOT_RUNNING [1]: ", default=1, choices=[0, 1])
SLEEP_TIME = prompt_int(f"SLEEP_TIME [{'5' if int(STOP_ON_NOT_RUNNING) == 1 else '30'}]: ", default=(5 if int(STOP_ON_NOT_RUNNING) == 1 else 30))
SHOW_URLS = prompt_int("SHOW_URLS [1]: ", default=1, choices=[0, 1])
SHOW_PROGRESS_BAR = prompt_int("SHOW_PROGRESS_BAR [1]: ", default=1, choices=[0, 1])
DECORATED_OUTPUT = prompt_int("DECORATED_OUTPUT [1]: ", default=1, choices=[0, 1])
TELEGRAM_BOT_TOKEN = prompt_string("TELEGRAM_BOT_TOKEN: ")
TELEGRAM_CHAT_ID = prompt_string("TELEGRAM_CHAT_ID: ")
TELEGRAM_MESSAGE = prompt_string("TELEGRAM_MESSAGE: ")

filename = f"jenkins-{JENKINS_PROJECT}"
bashCode = "\n".join(
    [
        "#!/bin/bash",
        "",
        "# script configuration",
        f'JENKINS_PROJECT="{JENKINS_PROJECT}"',
        f'JENKINS_EXTRA_JOBS="{JENKINS_EXTRA_JOBS}"',
        f'JENKINS_URL="{JENKINS_URL}"',
        f'JENKINS_USERNAME="{JENKINS_USERNAME}"',
        f'JENKINS_PASSWORD="{JENKINS_PASSWORD}"',
        f"STOP_ON_NOT_RUNNING={STOP_ON_NOT_RUNNING}",
        f"SLEEP_TIME={SLEEP_TIME}",
        f"SHOW_URLS={SHOW_URLS}",
        f"SHOW_PROGRESS_BAR={SHOW_PROGRESS_BAR}",
        f"DECORATED_OUTPUT={DECORATED_OUTPUT}",
        f'TELEGRAM_BOT_TOKEN="{TELEGRAM_BOT_TOKEN}"',
        f'TELEGRAM_CHAT_ID="{TELEGRAM_CHAT_ID}"',
        f'TELEGRAM_MESSAGE="{TELEGRAM_MESSAGE}"',
        "# end script configuration",
        "",
        'SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../main.py"',
        'python3 "$SCRIPT_PATH" "$JENKINS_PROJECT" "$JENKINS_EXTRA_JOBS" "$JENKINS_URL" "$JENKINS_USERNAME" "$JENKINS_PASSWORD" $SLEEP_TIME $SHOW_URLS "$TELEGRAM_BOT_TOKEN" "$TELEGRAM_CHAT_ID" "$TELEGRAM_MESSAGE" $DECORATED_OUTPUT $STOP_ON_NOT_RUNNING $SHOW_PROGRESS_BAR',
    ]
)

write_file(filename, bashCode, path='/'.join([os.getcwd(), 'scripts']))
