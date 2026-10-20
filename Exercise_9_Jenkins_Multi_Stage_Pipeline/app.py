from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    # In production/deployment, listen on 0.0.0.0:5000
    app.run(host="0.0.0.0", port=5000, debug=True)
