import environ
env = environ.Env()
environ.Env.read_env()

HOST = "https://group-13-epic-app.herokuapp.com" if env(
    "ENV") == "PROD" else "http://localhost:8000"
