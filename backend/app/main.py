from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.database import get_db 
import uvicorn
import os

app = FastAPI()

@app.get("/testar-banco")
def test_db_connection(db: Session = Depends(get_db)):
    try:
       
        db.execute(text("SELECT 1"))
        return {"status": "Sucesso", "mensagem": "Conectado ao Cloud SQL!"}
    except Exception as e:
        return {"status": "Erro", "detalhes": str(e)}

@app.get("/saude")
def health_check():
    return {"message": "API Online"}


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 8080))

    uvicorn.run("main:app", host="0.0.0.0", port=port)