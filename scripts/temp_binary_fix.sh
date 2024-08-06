#!/bin/bash

set -euo pipefail

sudo cp /opt/conda/lib/libstdc++.so.6.0.33 /usr/lib/aarch64-linux-gnu/
sudo cp /usr/lib/aarch64-linux-gnu/libstdc++.so.6 /usr/lib/aarch64-linux-gnu/libstdc++.so.6_OLD
sudo cp /usr/lib/aarch64-linux-gnu/libstdc++.so.6.0.33 /usr/lib/aarch64-linux-gnu/libstdc++.so.6
