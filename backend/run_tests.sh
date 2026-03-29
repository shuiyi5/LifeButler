#!/bin/bash
cd /Users/a1-6/Downloads/ageng-build-skill/LifeButler/backend
source ./venv/bin/activate
python -m pytest tests/unit/test_auth.py -v 2>&1
