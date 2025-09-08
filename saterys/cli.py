import argparse, os, subprocess, sys, time, webbrowser
from pathlib import Path
import uvicorn

def main():
    ap = argparse.ArgumentParser(prog="saterys", description="Saterys runner")
    ap.add_argument("--host", default=os.environ.get("SATERYS_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("SATERYS_PORT", "8000")))
    ap.add_argument("--dev", action="store_true", help="Run Vite (frontend) + Uvicorn (backend)")
    args = ap.parse_args()

    if args.dev:
        # Frontend path is inside package: saterys/web
        web_dir = Path(__file__).resolve().parent / "web"
        if (web_dir / "package.json").exists():
            os.environ.setdefault("SATERYS_DEV_ORIGIN", "http://localhost:5173")
            print("Starting Vite (frontend) on :5173")
            vite = subprocess.Popen(["npm", "run", "dev", "--", "--port=5173"], cwd=str(web_dir))
            time.sleep(1.0)
            try: webbrowser.open("http://localhost:5173")
            except Exception: pass
        else:
            print("No frontend found at saterys/web. Serving built assets only.")

    print(f"Starting Saterys API → http://{args.host}:{args.port}")
    uvicorn.run("saterys.app:app", host=args.host, port=args.port, reload=bool(args.dev))
