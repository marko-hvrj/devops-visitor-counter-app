#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <URL>"
    exit 1
fi

URL="$1"

for attempt in {1..5}; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

    echo "$(date '+%Y-%m-%d %H:%M:%S') - Attempt $attempt - HTTP $STATUS"

    if [ "$STATUS" = "200" ]; then
        exit 0
    fi

    if [ "$attempt" -lt 5 ]; then
        sleep 3
    fi
done

exit 1