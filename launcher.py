
# launcher.py
import subprocess
import time

# Run FastAPI
fastapi_process = subprocess.Popen(["uvicorn", "main:app", "--reload"])
print("FastAPI started...")
time.sleep(2)

# Run Streamlit
subprocess.run(["streamlit", "run", "app.py"])
