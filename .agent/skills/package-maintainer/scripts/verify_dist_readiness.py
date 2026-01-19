# scripts/verify_dist_readiness.py
import subprocess
import sys

def test_build():
    try:
        # Check if the project can be built into a wheel
        subprocess.run(["python", "-m", "build", "--wheel"], check=True, capture_output=True)
        print("✅ Package build successful.")
    except Exception as e:
        print(f"❌ Build Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_build()