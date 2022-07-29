#!/bin/sh

gunicorn --worker-class uvicorn.workers.UvicornWorker \
  --workers 2 \
  --bind 0.0.0.0:$NN_SERVER_PORT \
  notifications.main:create_app

# Run the main container process
exec "$@"
