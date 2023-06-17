import environ
env = environ.Env()
environ.Env.read_env()

HOST = "https://web-production-2f95.up.railway.app" if env(
    "ENV") == "PROD" else "http://localhost:8000"
