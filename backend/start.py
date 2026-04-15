"""
Wrapper de inicialização para Cloud Run.
Captura erros fatais e garante que o traceback seja logado
antes do container ser encerrado.
"""
import os
import sys
import time
import traceback

def main():
    try:
        print("=== STARTUP: importando app...", flush=True)
        from app.main import app  # noqa: F401
        print("=== STARTUP: import OK, iniciando uvicorn...", flush=True)

        import uvicorn
        port = int(os.environ.get("PORT", 8080))
        # Passar o objeto 'app' diretamente evita que o uvicorn faça um segundo __import__ por trás dos panos
        uvicorn.run(app, host="0.0.0.0", port=port)
    except BaseException as e:
        print(f"=== STARTUP CRASH: {type(e).__name__} ===", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.stderr.flush()
        sys.stdout.flush()
        # Mantém o container vivo por 30s para os logs serem capturados
        time.sleep(30)
        sys.exit(1)

if __name__ == "__main__":
    main()
