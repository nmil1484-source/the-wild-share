#!/bin/bash
exec python3 -m gunicorn --bind 0.0.0.0:$PORT src.main:app
