#!/bin/bash
echo "Stopping Portable SysAdmin Toolkit..."
pkill -f llama-server 2>/dev/null || true
echo "Done."
