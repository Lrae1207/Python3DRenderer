#!/bin/bash
# Linux only
# Check for dependencies
./scripts/download-dependencies.sh

if [ $? -eq 0 ]
then
    python3 engine.py
fi
