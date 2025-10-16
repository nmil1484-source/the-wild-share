#!/bin/bash
exec python3 -c "from src.main import app; app.run(host='0.0.0.0', port=int(__import__('os' ).environ.get('PORT', 5000)))"
