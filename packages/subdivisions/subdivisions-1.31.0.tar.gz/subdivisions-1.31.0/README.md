# Welcome to Subdivisions

[![PyPI](https://img.shields.io/pypi/v/subdivisions)](https://pypi.org/project/subdivisions/)
[![Publish](https://github.com/access55/subdivisions/workflows/publish/badge.svg)](https://github.com/access55/subdivisions/actions)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/subdivisions)](https://www.python.org)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[A55 Python library for PubSub Messaging](https://www.youtube.com/watch?v=EYYdQB0mkEU)

### Install in Project

```toml

# pyproject.toml
# Add in every project which will
# receive or send messages
[tool.subdivisions]
source_name = "ProjectName" # ex.: "Client-Manager"

[tool.poetry.dependencies]
subdivisions = "*"
```
Run `poetry update`

### Usage
#### Send Messages
```python
from subdivisions.client import SubClient
from subdivisions.events import UserEvents

client = SubClient()
client.topic = UserEvents.USER_REGISTERED
client.send({"foo": "bar"})
```

#### Receive Messages
```python
from subdivisions.client import SubClient
from subdivisions.events import UserEvents

client = SubClient()
client.topic = UserEvents.USER_REGISTERED
messages = client.get_messages()  # use the ``from_dead_letter=True` to receive Dead Letter messages
# Process messages
client.delete_received_messages()
```

### Full Configuration options

Configure subdivisions options in `pyproject.toml` file, inside `[tool.subdivisions]` table:

```toml
# pyproject.toml
[tool.subdivisions]
aws_region = "us-east-1"            # AWS Region
aws_allowed_account = ""            # AWS Allowed Account Id for create artifacts / send messages
pub_key = "alias/PubSubKey"         # KMS PubSubKey (must be created first)
sqs_tags = []                       # SQS tags for new queues. Example [{"foo": "bar"}]
queue_prefix = ""                   # Prefix for new SQS queues
queue_suffix = ""                   # Suffix for new SQS queues
queue_max_receive_count = 1000      # SQS MaxReceiveCount setting
sns_prefix = ""                     # Prefix for new SNS topics
sns_suffix = ""                     # Suffix for new SNS topics
sns_tags = []                       # SNS tags for new topics. Example [{"foo": "bar"}]
event_prefix = ""                   # Prefix for new Eventbride rules
event_suffix = ""                   # Suffix for new Eventbride rules
event_tags = []                     # Eventbridge tags for new rules. Example [{"foo": "bar"}]
event_bus = "default"               # Eventbridge Bus
source_name = ""                    # Eventbridge default source name. No default, must inform
auto_create_new_topic = true        # Auto create new topic if not exists in Eventbridge
auto_remove_from_queue = false      # Acknowledge first messages on receive
use_aws_env_vars = true             # Use AWS default env vars. If false append "SUBDIVISION_" on env vars. Example: "SUBDIVISION_AWS_ACCESS_KEY_ID"
default_prefix = "a55"              # Default prefix for all sns, sqs and rule created
default_suffix = ""                 # Default suffix for all sns, sqs and rule created
```

All options above can be configured in environment variables. Just append `SUBDIVISIONS_` on name. Example: `SUBDIVISIONS_SOURCE_NAME="my_project"`

### Local Development

For local development, please first clone and install this project:

```shell
git clone git@github.com:access55/subdivisions.git /path/to/project
cd /path/to/project

# Install on WSL/Linux
make install

# Install on Powershell
poetry install
```


#### Example: Adding a new Topic
To avoid different names in different projects for the same topic, (i.e: "client_registered" and
"customer_registered") please add new events using Python Enum on `subdivisions.event` module:

```python
# subdivisions.events
from enum import unique, Enum

@unique
class MyNewEvents(Enum):
    MY_NEW_EVENT = "my_new_event"
```

#### Commit using a conventional commit message

To generate a new PyPI version, at least one commit must following the
[Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/) Specification, when you can
add the `feat:` or `fix:` prefix in your message:

```shell
# Create a new patch event. Ex. 1.0.0 to 1.0.1
git commit -m "fix: Event Bug"

# Create a new minor event. Ex. 1.0.0 to 1.1.0
git commit -m "feat: Add New Event"

# Create a new major event. Ex. 1.0.0 to 2.0.0
git commit -m "feat!: Add New Event \n\nBREAKING CHANGE: API changed"
```
Without a `feat:` or `fix:` prefixed commited message, code will not generate a new PyPI version.

### Using AWS Credentials locally

Subdivisions will use AWS default environment variables. If you need to define another credentials, use the following variables:

```env
SUBDIVISIONS_USE_AWS_ENV_VARS="false"
SUBDIVISIONS_AWS_ACCESS_KEY_ID="your id"
SUBDIVISIONS_AWS_SECRET_ACCESS_KEY="your key"
SUBDIVISIONS_AWS_SESSION_TOKEN="your token" # optional
```
