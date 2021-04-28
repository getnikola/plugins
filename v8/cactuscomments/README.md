Use [Cactus Comments](https://cactus.chat/) as a comment system.

[Cactus Comments](https://cactus.chat/) is a federated comment system for the web,
based on the [Matrix](https://matrix.org) protocol.
Users can comment as guest on the configured default homeserver
(which should also run the Cactus Comments application service),
or with an account on any Matrix homeserver.

The settings for [Cactus Comments](https://cactus.chat) can be passed to the plugin as follows
(see the [quickstart guide](https://cactus.chat/docs/getting-started/quick-start/)
and [configuration reference](https://cactus.chat/docs/reference/web-client/#configuration)
for more details, including the full list of configuration options):

```python
COMMENT_SYSTEM = "cactus"
COMMENT_SYSTEM_ID = "<YOUR-SITE_NAME>"
GLOBAL_CONTEXT = {
    ...
    "cactus_config": {
        "defaultHomeserverUrl": "https://matrix.cactus.chat:8448",
        "serverName": "cactus.chat"
        }
    }
```
