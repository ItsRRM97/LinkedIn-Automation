#!/bin/bash
# Deprecated — forwards to publish-day schedule installer.
set -euo pipefail
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/install_publish_day_schedule.sh"
