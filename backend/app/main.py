from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Online", "projeto": "Dog-Mau-AutoCenter"}

@app.get("/saude")
def health_check():
    return {"message": "Tudo certo por aqui!"}