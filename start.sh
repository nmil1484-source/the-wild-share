#!/bin/bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m gunicorn --bind 0.0.0.0:$PORT src.main:app
