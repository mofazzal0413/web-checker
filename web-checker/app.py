from selenium_test import run_selenium_smoke_test
import os
from flask import Flask, render_template, request, Response
import requests
import time
import csv
from io import StringIO

# Detect Render environment
RUNNING_ON_RENDER = os.environ.get("RENDER") == "true"

app = Flask(__name__)

# ---------------- CSV EXPORT ROUTE ----------------
@app.route("/export_csv")
def export_csv():
    results = app.config.get("LAST_RESULTS", [])

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["URL", "Status", "Message"])

    for r in results:
        writer.writerow([r["url"], r["status"], r["message"]])

    output = si.getvalue()
    si.close()

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=results.csv"}
    )

# ---------------- URL CHECK FUNCTION ----------------
def check_single_url(url):
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    result = {"url": url}

    try:
        start = time.time()
        response = requests.get(url, timeout=5, allow_redirects=True)
        end = time.time()

        result["response_time"] = int((end - start) * 1000)
        result["status_code"] = response.status_code

        if response.status_code == 200:
            result["status"] = "PASS"
            result["message"] = f"200 OK — {result['response_time']}ms"
        else:
            result["status"] = "FAIL"
            result["message"] = f"Status {response.status_code} — {result['response_time']}ms"

    except requests.exceptions.ConnectionError:
        result["status"] = "FAIL"
        result["message"] = "Connection failed"

    except requests.exceptions.Timeout:
        result["status"] = "FAIL"
        result["message"] = "Request timed out"

    except requests.exceptions.InvalidURL:
        result["status"] = "FAIL"
        result["message"] = "Invalid URL"

    except requests.exceptions.InvalidSchema:
        result["status"] = "FAIL"
        result["message"] = "Invalid URL format"

    except Exception as e:
        result["status"] = "FAIL"
        result["message"] = f"Error: {str(e)}"

    return result

# ---------------- MAIN ROUTE ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    results = []

    if request.method == "POST":
        urls_text = request.form.get("urls", "").strip()

        if not urls_text:
            results.append({"url": "None", "status": "FAIL", "message": "No URL provided"})
        else:
            urls = urls_text.split("\n")
            for url in urls:
                if url.strip():
                    # Normal HTTP check
                    results.append(check_single_url(url))

                    # Selenium smoke test (LOCAL ONLY)
                    if not RUNNING_ON_RENDER:
                        selenium_result = run_selenium_smoke_test(url)
                        results.append(selenium_result)
                    else:
                        results.append({
                            "url": url,
                            "status": "SKIPPED",
                            "message": "Selenium disabled on Render"
                        })

        app.config["LAST_RESULTS"] = results

    return render_template("index.html", results=results)

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
