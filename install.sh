#!/usr/bin/env bash
echo "Installing ProfileSizeTest requirements..."
if command -v pip3 >/dev/null 2>&1; then
    pip3 install -r requirements.txt --user || true
elif command -v pip >/dev/null 2>&1; then
    pip install -r requirements.txt --user || true
fi
echo "Installation complete."
exit 0
