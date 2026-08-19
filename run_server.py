import sys
sys.path.insert(0, '.')
import app.main
import uvicorn
uvicorn.run(app.main.app, host='0.0.0.0', port=8000, log_level='info')