from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db 

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