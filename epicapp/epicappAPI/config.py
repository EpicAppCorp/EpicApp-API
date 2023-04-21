import environ
env = environ.Env()
environ.Env.read_env()

HOST = "https://epicapp-api.onrender.com" if env(
    "ENV") == "PROD" else "http://localhost:8000"
