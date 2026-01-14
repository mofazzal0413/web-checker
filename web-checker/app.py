from flask import Flask, render_template, request
import requests
import time

app = Flask(__name__)

def check_single_url(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        end = time.time()

        response_time = int((end - start) * 1000)  # convert to ms

        if response.status_code == 200:
            return "PASS", f"200 OK — {response_time}ms"
        else:
            return "FAIL", f"Status {response.status_code} — {response_time}ms"

    except Exception as e:
        return "FAIL", f"{str(e)}"


@app.route("/", methods=["GET", "POST"])
def home():
    results = []

    if request.method == "POST":
        urls_text = request.form.get("urls")

        if not urls_text:
            results.append(("No URL provided", "FAIL"))
            return render_template("index.html", results=results)

        # Split URLs by new line
        urls = urls_text.strip().split("\n")

        for url in urls:
            url = url.strip()
            if url:
                status, message = check_single_url(url)
                results.append((url, f"{status}: {message}"))

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
