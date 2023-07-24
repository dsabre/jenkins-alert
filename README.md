# jenkins-alert

A simple Jenkins watcher in python.

## Requirements

- [notify-send](https://ss64.com/bash/notify-send.html "notify-send")
- [tabulate](https://pypi.org/project/tabulate/ "tabulate")

## Usage

Create a script inside the scripts directory with the following code (try the versions to find what fits to you):

Old version

```bash
#!/bin/bash

# script configuration
JENKINS_PROJECT="project-name"
JENKINS_PROMOTION_STAGE_NAME="promotion-stage-name"
JENKINS_PROMOTION_PROD_NAME="promotion-prod-name"
JENKINS_URL="http://your-jenkins-url.example"
JENKINS_USERNAME="username"
JENKINS_PASSWORD="password"
SLEEP_TIME=5 # info refresh timing expressed in seconds
TELEGRAM_BOT_TOKEN="" # optional
TELEGRAM_CHAT_ID="" # optional
TELEGRAM_MESSAGE="" # optional (if empty but telegram is configured, will be used a standard message)
# end script configuration

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../main.py"

python3 "$SCRIPT_PATH" "$JENKINS_PROJECT" "$JENKINS_PROMOTION_STAGE_NAME" "$JENKINS_PROMOTION_PROD_NAME" "$JENKINS_URL" "$JENKINS_USERNAME" "$JENKINS_PASSWORD" $SLEEP_TIME "$TELEGRAM_BOT_TOKEN" "$TELEGRAM_CHAT_ID" "$TELEGRAM_MESSAGE"
```

New version:

```bash
#!/bin/bash

# script configuration
JENKINS_PROJECT="project-name|split-by-pipes"
JENKINS_URL="http://your-jenkins-url.example"
JENKINS_USERNAME="username"
JENKINS_PASSWORD="password"
SLEEP_TIME=5 # info refresh timing expressed in seconds
TELEGRAM_BOT_TOKEN="" # optional
TELEGRAM_CHAT_ID="" # optional
TELEGRAM_MESSAGE="" # optional (if empty but telegram is configured, will be used a standard message)
# end script configuration

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../new.py"

python3 "$SCRIPT_PATH" "$JENKINS_PROJECT" "$JENKINS_URL" "$JENKINS_USERNAME" "$JENKINS_PASSWORD" $SLEEP_TIME "$TELEGRAM_BOT_TOKEN" "$TELEGRAM_CHAT_ID" "$TELEGRAM_MESSAGE"
```
