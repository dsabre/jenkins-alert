# jenkins-alert

A simple Jenkins watcher in python.

## Requirements

- [notify-send](https://ss64.com/bash/notify-send.html "notify-send")
- [tabulate](https://pypi.org/project/tabulate/ "tabulate")

## Usage

Create a script inside the scripts directory with the following code:

```bash
#!/bin/bash

# script configuration
JENKINS_PROJECT="project-name|split-by-pipes-if-you-have-groups"
JENKINS_EXTRA_JOBS="extra-jobs|split-by-pipes" # can be empty
JENKINS_URL="http://your-jenkins-url.example"
JENKINS_USERNAME="username"
JENKINS_PASSWORD="password"
SLEEP_TIME=5 # info refresh timing expressed in seconds
TELEGRAM_BOT_TOKEN="" # can be empty
TELEGRAM_CHAT_ID="" # can be empty
TELEGRAM_MESSAGE="" # can be empty (if empty but telegram is configured, will be used a standard message)
# end script configuration

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../main.py"

python3 "$SCRIPT_PATH" "$JENKINS_PROJECT" "$JENKINS_EXTRA_JOBS" "$JENKINS_URL" "$JENKINS_USERNAME" "$JENKINS_PASSWORD" $SLEEP_TIME "$TELEGRAM_BOT_TOKEN" "$TELEGRAM_CHAT_ID" "$TELEGRAM_MESSAGE"
```
