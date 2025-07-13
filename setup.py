from setuptools import setup, find_packages
import subprocess
import sys

def install_dependencies():
    print("Installing required packages...")
    packages = [
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
        "sqlalchemy",
        "beautifulsoup4",
        "transformers",
        "torch",
        "sentencepiece",
        "spacy",
        "streamlit>=1.32.0",
        "python-dotenv>=1.0.0",
        "plotly",
        "pandas"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\nInstalling spaCy English language model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

if __name__ == "__main__":
    install_dependencies()
    print("\nSetup completed successfully! You can now run the application using:")
    print("streamlit run streamlit_app.py") 