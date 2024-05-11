#!/bin/bash
# Linux only/run by sudo
# Check for dependencies
chmod +x ./scripts/download-dependencies.sh
sudo ./scripts/download-dependencies.sh

if [ $? -eq 0 ]
then
    python3 engine.py
fi
