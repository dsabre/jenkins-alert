# jenkins-alert

## Usage

Create a script inside the scripts directory with the following code:

```bash
#!/bin/bash

SCRIPT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )/../main.py"

python3 "$SCRIPT_PATH" "project-name" "promotion-stage-name" "promotion-prod-name" "http://your-jenkins-url.example" "username" "password" 5
```

The la st number in the script above is the refresh timing expressed in seconds.
