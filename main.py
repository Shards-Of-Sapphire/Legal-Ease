from app import app

if __name__ == "__main__":
    app.run()

@app.route("/")
def home():
    return "LegalEase backend is running."
