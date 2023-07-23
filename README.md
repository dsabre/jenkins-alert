# jenkins-alert

## Usage

Create a script inside the scripts directory with the following code:

```bash
#!/bin/bash

# script configuration
JENKINS_PROJECT="project-name"
JENKINS_PROMOTION_STAGE_NAME="promotion-stage-name"
JENKINS_PROMOTION_PROD_NAME="promotion-prod-name"
JENKINS_URL="http://your-jenkins-url.example"
JENKINS_USERNAME="username"
JENKINS_PASSWORD="password"
SLEEP_TIME=5
# end script configuration

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../main.py"

python3 "$SCRIPT_PATH" "$JENKINS_PROJECT" "$JENKINS_PROMOTION_STAGE_NAME" "$JENKINS_PROMOTION_PROD_NAME" "$JENKINS_URL" "$JENKINS_USERNAME" "$JENKINS_PASSWORD" $SLEEP_TIME
```

The SLEEP_TIME in the script above is the refresh timing expressed in seconds.
