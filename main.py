from core.app_controller import AppController

def main()->int:
    app=AppController(); app.start(); return 0

if __name__=='__main__':
    raise SystemExit(main())
