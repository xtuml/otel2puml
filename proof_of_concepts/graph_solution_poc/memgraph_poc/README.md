# Note

To be able to connect to the memgraph docker container, you must create a network that both the dev container and memgraph container use.

The following has to be added to the devcontainer.json
```json
"runArgs": [
    "--network=<custom_network>"
],
```