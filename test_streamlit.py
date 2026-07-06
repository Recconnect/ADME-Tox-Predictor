import subprocess
import time
import requests

# Запускаем streamlit в фоне
proc = subprocess.Popen(
    [r"D:\AI\biotech\adme_proto\venv\Scripts\streamlit.exe", "run", "app.py", 
     "--server.port=8501", "--server.headless=true"],
    cwd=r"D:\AI\biotech\adme_proto",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8',
    errors='replace'
)

print("Waiting for Streamlit to start...")
time.sleep(5)

# Проверяем, запущен ли процесс
if proc.poll() is None:
    print("Streamlit process is running")
else:
    print(f"Streamlit process exited with code: {proc.returncode}")
    output = proc.stdout.read()
    print(f"Output: {output}")
    exit(1)

# Пробуем сделать запрос
try:
    response = requests.get("http://localhost:8501", timeout=5)
    print(f"HTTP Status: {response.status_code}")
    print(f"Content Length: {len(response.text)}")
    print("SUCCESS: Streamlit is responding!")
except Exception as e:
    print(f"FAILED to connect: {e}")
    # Читаем вывод streamlit
    proc.terminate()
    output = proc.stdout.read()
    print(f"Streamlit output:\n{output}")
    exit(1)

# Останавливаем процесс
proc.terminate()
proc.wait()
print("Test completed successfully!")
