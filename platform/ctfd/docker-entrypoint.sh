#!/bin/bash
set -e

# Patch CTFd's __init__.py to remove the init_plugins import
# This line tries to import init_plugins which doesn't exist in the current version
sed -i 's/from CTFd.plugins import init_plugins/#from CTFd.plugins import init_plugins/' /opt/CTFd/CTFd/__init__.py

# Also comment out where init_plugins is used
sed -i 's/init_plugins(app)/#init_plugins(app)/' /opt/CTFd/CTFd/__init__.py

# Now run the original CTFd entrypoint
exec /opt/CTFd/docker-entrypoint.sh "$@"