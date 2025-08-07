
import subprocess

import time

#api run
fastapi_process = subprocess.Popen(["uvicorn", "main:app", "--reload"])
print("FastAPI started...")
time.sleep(2)

#streamlit run
subprocess.run(["streamlit", "run", "app.py"])
