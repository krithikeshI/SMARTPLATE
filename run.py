import sys, os
sys.path.append(os.path.dirname(__file__))  # ✅ ensures smartplate package is seen

from smartplate.main import start_application

if __name__ == "__main__":
    start_application()
