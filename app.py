from flask import Flask, request, render_template_string
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200000

# Detection rules
patterns = [
    {
        "name": "Instruction Override",
        "pattern": r"ignore (all )?(previous|prior) instructions",
        "severity": "High"
    },
    {
        "name": "Secret Disclosure",
        "pattern": r"(reveal|show|print|expose).{0,30}(password|secret|system prompt|API key)",
        "severity": "High"
    },
    {
        "name": "Security Bypass",
        "pattern": r"(bypass|disable|evade).{0,30}(security|safety|authentication)",
        "severity": "High"
    },
    {
        "name": "Confidential Data Transfer",
        "pattern": r"(send|share|transfer|upload).{0,30}(confidential|private|sensitive) data",
        "severity": "High"
    }
]


def scan_text(text):
    findings = []

    for line_number, line in enumerate(text.splitlines(), 1):
        for item in patterns:
            for match in re.finditer(
                item["pattern"], line, re.IGNORECASE
            ):
                findings.append({
                    "name": item["name"],
                    "severity": item["severity"],
                    "line": line_number,
                    "matched_text": match.group(),
                    "context": line.strip()
                })

    return findings


def calculate_risk(findings):
    if any(f["severity"] == "High" for f in findings):
        return "High", 85
    if any(f["severity"] == "Moderate" for f in findings):
        return "Moderate", 55
    if findings:
        return "Low", 20
    return "Safe", 0


HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ThreatLens | Document Security Scanner</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #10101b;
    color: #f4f0ff;
}

header {
    padding: 25px 8%;
    border-bottom: 1px solid #29253c;
    background: #151322;
}

header h1 {
    margin: 0;
    color: #c4b5fd;
    letter-spacing: 1px;
}

header p {
    color: #a6a2b8;
    margin-bottom: 0;
}

main {
    max-width: 1000px;
    margin: 45px auto;
    padding: 0 20px;
}

.panel {
    background: #191827;
    border: 1px solid #302b48;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
    box-shadow: 0 10px 35px #00000020;
}

h2 { margin-top: 0; }

.muted { color: #a6a2b8; }

input[type=file] {
    width: 100%;
    padding: 15px;
    margin: 18px 0;
    background: #11101c;
    color: white;
    border: 1px solid #45405f;
    border-radius: 10px;
}

button {
    background: #8b5cf6;
    color: white;
    padding: 13px 24px;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
}

button:hover { background: #7c3aed; }

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 15px;
}

.stat {
    padding: 18px;
    background: #11101c;
    border: 1px solid #302b48;
    border-radius: 12px;
}

.stat h3 {
    color: #c4b5fd;
    margin-bottom: 8px;
}

.stat p {
    font-size: 23px;
    font-weight: bold;
    margin: 0;
    overflow-wrap: anywhere;
}

.progress {
    height: 10px;
    background: #302b48;
    border-radius: 10px;
    margin-top: 12px;
    overflow: hidden;
}

.bar {
    height: 100%;
    background: #a78bfa;
    transition: width 0.5s;
}

.finding {
    padding: 18px;
    margin-top: 14px;
    border: 1px solid #45405f;
    border-radius: 12px;
    background: #131220;
    overflow-wrap: anywhere;
}

.severity {
    color: #fca5a5;
    font-weight: bold;
}

code {
    color: #ddd6fe;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.result-note {
    color: #b9b4ca;
    line-height: 1.6;
}

footer {
    text-align: center;
    color: #858097;
    padding: 25px;
}

@media (max-width: 600px) {
    .panel { padding: 20px; }
    main { margin-top: 25px; }
}
</style>
</head>

<body>
<header>
    <h1>ThreatLens</h1>
    <p>Document Security and Suspicious Instruction Scanner</p>
</header>

<main>
    <section class="panel">
        <h2>Scan a document</h2>
        <p class="muted">
            Upload a TXT file to check for suspicious instruction patterns.
        </p>

        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="document" accept=".txt" required>
            <button type="submit">Scan Document</button>
        </form>

        <p class="muted">
            Maximum file size: approximately 195 KiB. TXT files only.
        </p>
    </section>

    {% if result %}
    <section class="panel">
        <h2>Scan Results</h2>
        <p class="muted">File: {{ filename | e }}</p>
        <p>{{ result | e }}</p>

        <div class="stats">
            <div class="stat">
                <h3>Risk Level</h3>
                <p>{{ risk | e }}</p>
            </div>

            <div class="stat">
                <h3>Risk Score</h3>
                <p>{{ score }}/100</p>
                <div class="progress">
                    <div class="bar" style="width: {{ score }}%"></div>
                </div>
            </div>

            <div class="stat">
                <h3>Findings</h3>
                <p>{{ findings | length }}</p>
            </div>
        </div>

        <h3 style="margin-top:28px">Detection Summary</h3>
        <p>{{ category | e }}</p>

        <h3>Recommended Action</h3>
        <p class="result-note">{{ action | e }}</p>

        {% if findings %}
        <h3 style="margin-top:28px">
            Detected Findings ({{ findings | length }})
        </h3>

        {% for finding in findings %}
        <div class="finding">
            <h3>{{ finding.name | e }}</h3>

            <p class="severity">
                Severity: {{ finding.severity | e }}
            </p>

            <p>Line: {{ finding.line }}</p>

            <p>Matched text:</p>
            <code>{{ finding.matched_text | e }}</code>

            <p class="muted">Context:</p>
            <code>{{ finding.context | e }}</code>
        </div>
        {% endfor %}

        {% else %}
        <p class="result-note">
            No suspicious phrases matched the current detection rules.
            This does not guarantee that the document is safe.
        </p>
        {% endif %}
    </section>
    {% endif %}

    <section class="panel">
        <h2>About ThreatLens</h2>
        <p class="muted">
            ThreatLens checks document text against a set of predefined
            patterns that may indicate instruction overrides, secret
            disclosure attempts, security bypasses, or confidential data
            transfer instructions.
        </p>
        <p class="muted">
            This is a basic pattern-based prototype, not an antivirus
            scanner or a complete security assessment.
        </p>
    </section>
</main>

<footer>ThreatLens · Document Security Prototype</footer>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    filename = ""
    risk = "Not scanned"
    score = 0
    category = "None"
    action = "Upload a document to begin"
    findings = []

    if request.method == "POST":
        file = request.files.get("document")

        if not file or not file.filename:
            result = "Please select a document."
            risk = "Unknown"
            category = "Missing document"
            action = "Choose a TXT file"

        elif not file.filename.lower().endswith(".txt"):
            result = "Only TXT files are supported."
            risk = "Unknown"
            category = "Unsupported file"
            action = "Choose a TXT file"

        else:
            filename = file.filename
            raw_text = file.read(200001)

            if len(raw_text) > 200000:
                result = "The file is too large."
                risk = "Unknown"
                category = "File size limit exceeded"
                action = "Choose a smaller TXT file"

            else:
                text = raw_text.decode("utf-8", errors="replace")

                findings = scan_text(text)
                risk, score = calculate_risk(findings)

                if findings:
                    category = (
                        f"{len(findings)} suspicious pattern(s) detected"
                    )
                    result = (
                        "Review the detected findings below."
                    )
                    action = (
                        "Hold the document for manual security review"
                    )
                else:
                    category = "No known pattern matched"
                    result = (
                        "No matching suspicious phrase was found."
                    )
                    action = (
                        "Run additional security checks before ingestion"
                    )

    return render_template_string(
        HTML,
        result=result,
        filename=filename,
        risk=risk,
        score=score,
        category=category,
        action=action,
        findings=findings
    )


if __name__ == "__main__":
    app.run(debug=True)
