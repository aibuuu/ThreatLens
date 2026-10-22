from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import re
from datetime import datetime

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200_000

RULES = [
    ("Instruction Override",
     r"ignore (all )?(previous|prior) instructions", "HIGH", 30),
    ("System Prompt Disclosure",
     r"(reveal|show|print|expose).{0,40}(system prompt|password|secret|api key)",
     "HIGH", 30),
    ("Security Bypass",
     r"(bypass|disable|evade).{0,40}(security|safety|authentication)",
     "HIGH", 25),
    ("Confidential Data Transfer",
     r"(send|share|transfer|upload).{0,40}(confidential|private|sensitive) data",
     "HIGH", 25),
    ("Role Manipulation",
     r"(act as|pretend to be|you are now) .{0,50}(admin|system|developer)",
     "MEDIUM", 15),
    ("Instruction Concealment",
     r"(do not tell|hide this from|keep this secret from)",
     "MEDIUM", 15),
    ("Data Exfiltration",
     r"(extract|dump|exfiltrate).{0,40}(data|records|credentials)",
     "HIGH", 25),
]

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ThreatLens // Security Intelligence</title>
<style>
:root {
 --bg:#080910; --panel:#10121e; --panel2:#141727;
 --purple:#a855f7; --cyan:#22d3ee; --text:#edf1ff;
 --muted:#858ca8; --line:#252940; --red:#fb5475;
 --green:#4adea5; --yellow:#fbbf24;
}
* { box-sizing:border-box; }
body {
 margin:0; color:var(--text); background:
 radial-gradient(ellipse at 80% 0%,#27123d55,transparent 40%),
 radial-gradient(ellipse at 0% 35%,#07304435,transparent 35%),
 var(--bg); font-family:Inter,Segoe UI,Arial,sans-serif;
 min-height:100vh;
}
body:before {
 content:""; position:fixed; inset:0; pointer-events:none;
 background-image:linear-gradient(#ffffff04 1px,transparent 1px),
 linear-gradient(90deg,#ffffff04 1px,transparent 1px);
 background-size:40px 40px; z-index:-1;
}
button,input { font:inherit; }
.layout { display:flex; min-height:100vh; }
.sidebar {
 width:245px; flex-shrink:0; background:#0b0c15eF;
 border-right:1px solid var(--line); padding:26px 17px;
 display:flex; flex-direction:column;
}
.brand { display:flex; align-items:center; gap:12px; padding:4px 8px 30px; }
.logo {
 width:39px;height:39px;border-radius:12px;display:grid;place-items:center;
 color:#fff;font-size:22px;font-weight:900;
 background:linear-gradient(135deg,var(--purple),#5125a7);
 box-shadow:0 0 25px #a855f744;
}
.brand h2 { margin:0;font-size:17px;letter-spacing:2px; }
.brand small { color:var(--cyan);font-size:9px;letter-spacing:2px; }
.navtitle { font-size:10px;color:#666e8d;letter-spacing:2px;padding:12px; }
.nav {
 display:flex;gap:12px;align-items:center;padding:13px 12px;
 border-radius:9px;color:#a5abc3;margin-bottom:5px;font-size:13px;
}
.nav.active { color:#e9d5ff;background:#a855f71a;border:1px solid #a855f733; }
.nav .ico { width:19px;text-align:center;color:var(--cyan); }
.sidebottom { margin-top:auto; }
.connection {
 border:1px solid var(--line);border-radius:12px;padding:14px;
 background:#111321;
}
.dot { display:inline-block;width:7px;height:7px;border-radius:50%;
 background:var(--green);box-shadow:0 0 10px var(--green);margin-right:7px; }
.connection p { color:var(--muted);font-size:11px;margin:9px 0 0;line-height:1.6; }
main { flex:1;min-width:0;padding:28px 35px 45px;max-width:1600px;margin:auto;width:100%; }
.topbar { display:flex;justify-content:space-between;align-items:center;gap:14px;
 border-bottom:1px solid var(--line);padding-bottom:20px;margin-bottom:28px; }
.eyebrow { color:var(--cyan);font-size:10px;letter-spacing:2px;font-weight:700; }
.topbar h1 { font-size:24px;margin:8px 0 0;letter-spacing:-.6px; }
.topright { display:flex;align-items:center;gap:10px; }
.pill { border:1px solid var(--line);background:#121421;padding:9px 12px;
 border-radius:30px;color:#b9c0d9;font-size:11px; }
.hero { display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin-bottom:23px; }
.hero h2 { font-size:clamp(24px,3vw,35px);margin:9px 0;letter-spacing:-1px; }
.hero h2 span { color:var(--purple); }
.hero p { color:var(--muted);font-size:13px;line-height:1.7;max-width:610px;margin:0; }
.badge { color:var(--green);border:1px solid #4adea533;background:#4adea50d;
 padding:8px 11px;border-radius:7px;font-size:10px;white-space:nowrap; }
.metrics { display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:22px 0; }
.metric,.card { background:linear-gradient(145deg,#141626,#0e101a);
 border:1px solid var(--line);border-radius:13px; }
.metric { padding:19px;position:relative;overflow:hidden; }
.metric:after { content:"";position:absolute;top:0;left:0;width:55px;height:2px;background:var(--purple); }
.metric:nth-child(2):after { background:var(--cyan); }
.metric:nth-child(3):after { background:var(--red); }
.metric:nth-child(4):after { background:var(--green); }
.mlabel { color:var(--muted);font-size:11px; }
.mvalue { font-size:27px;font-weight:750;margin:13px 0 7px;letter-spacing:-1px; }
.mnote { color:#7d86a4;font-size:10px; }
.contentgrid { display:grid;grid-template-columns:minmax(0,1.5fr) minmax(260px,.85fr);gap:17px; }
.card { padding:22px;margin-bottom:17px;min-width:0; }
.cardhead { display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:17px; }
.cardhead h3 { font-size:14px;margin:0; }
.sub { color:var(--muted);font-size:11px;margin-top:7px;line-height:1.6; }
.tag { font-size:9px;letter-spacing:1px;color:var(--cyan);border:1px solid #22d3ee33;padding:6px 8px;border-radius:5px; }
.drop {
 display:block;text-align:center;padding:30px 16px;border:1px dashed #5b4c86;
 background:linear-gradient(140deg,#a855f70c,#22d3ee07);border-radius:12px;
 cursor:pointer;transition:.2s;
}
.drop:hover,.drop.drag { border-color:var(--cyan);background:#22d3ee0d; }
.uploadicon { font-size:29px;color:var(--cyan);margin-bottom:12px; }
.drop strong { display:block;font-size:13px; }
.drop p { color:var(--muted);font-size:11px;line-height:1.6; }
.drop b { color:#d8b4fe; }
input[type=file] { position:absolute;width:1px;height:1px;opacity:0; }
.fileinfo { margin-top:12px;color:var(--cyan);font-size:11px;overflow-wrap:anywhere; }
.btn {
 border:0;border-radius:8px;padding:13px 18px;font-size:12px;font-weight:800;
 color:#fff;cursor:pointer;background:linear-gradient(100deg,#7c3aed,#a855f7);
 box-shadow:0 5px 22px #9333ea30;transition:.2s;
}
.btn:hover { transform:translateY(-1px);box-shadow:0 6px 25px #9333ea55; }
.btn:disabled { opacity:.65;cursor:wait; }
.full { width:100%;margin-top:15px; }
.smallnote { color:#6f7794;font-size:10px;line-height:1.7;margin-top:12px; }
.scanline {
 height:5px;background:#252940;border-radius:5px;overflow:hidden;margin-top:14px;
}
.scanline span { display:block;width:35%;height:100%;background:var(--cyan);
 box-shadow:0 0 12px var(--cyan);animation:scan 1.2s linear infinite; }
@keyframes scan { from{transform:translateX(-120%)}to{transform:translateX(400%)} }
.hidden { display:none; }
.riskwrap { display:flex;align-items:center;gap:18px; }
.gauge { width:115px;height:115px;border-radius:50%;display:grid;place-items:center;
 background:conic-gradient(var(--purple) calc(var(--score)*1%),#272940 0);
 position:relative;flex-shrink:0; }
.gauge:before { content:"";position:absolute;inset:8px;border-radius:50%;background:#11121f; }
.gaugeinner { position:relative;text-align:center; }
.gaugeinner strong { font-size:28px;display:block; }
.gaugeinner small { color:var(--muted);font-size:9px;letter-spacing:1px; }
.risklabel { font-size:19px;font-weight:800;margin-bottom:8px; }
.risklabel.HIGH { color:var(--red); }
.risklabel.MEDIUM { color:var(--yellow); }
.risklabel.LOW { color:var(--green); }
.risklabel.SAFE { color:var(--cyan); }
.resultmessage { color:var(--muted);font-size:11px;line-height:1.7; }
.resultstats { display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:20px; }
.rstat { background:#090b14;border:1px solid var(--line);border-radius:8px;padding:12px; }
.rstat strong { display:block;font-size:19px;margin-bottom:5px; }
.rstat span { font-size:9px;color:var(--muted); }
.finding { border:1px solid var(--line);background:#0b0d17;border-radius:10px;padding:15px;margin-top:11px; }
.fhead { display:flex;justify-content:space-between;align-items:center;gap:8px; }
.fhead strong { font-size:12px; }
.sev { font-size:9px;font-weight:800;letter-spacing:1px;padding:5px 7px;border-radius:4px; }
.sev.HIGH { color:#ff8fa5;background:#fb54751a; }
.sev.MEDIUM { color:#fcd34d;background:#fbbf2417; }
.fmeta { color:var(--muted);font-size:10px;margin:10px 0; }
.matched { color:#f0abfc;font-family:Consolas,monospace;font-size:11px;overflow-wrap:anywhere; }
.context { color:#abb3ce;background:#131626;padding:10px;border-radius:6px;
 margin-top:9px;font-family:Consolas,monospace;font-size:11px;white-space:pre-wrap;overflow-wrap:anywhere; }
.empty { text-align:center;padding:23px;color:var(--muted);font-size:12px;line-height:1.8; }
.empty strong { color:var(--green);display:block;font-size:14px;margin-bottom:6px; }
.alert { border:1px solid #fb547555;background:#fb54750c;color:#ffb3c1;
 padding:13px;border-radius:8px;margin-bottom:15px;font-size:12px; }
.footer { text-align:center;color:#5f6681;font-size:10px;padding:22px; }
@media(max-width:1000px) {
 .sidebar { width:75px;padding:22px 10px; }
 .brand { justify-content:center;padding:4px 0 30px; }
 .brandtext,.navtitle,.navtext,.sidebottom { display:none; }
 .nav { justify-content:center;padding:13px 4px; }
 main { padding:22px 20px; }
 .metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
 .contentgrid { grid-template-columns:1fr; }
}
@media(max-width:580px) {
 .sidebar { display:none; }
 main { padding:18px 12px; }
 .topbar { align-items:flex-start; }
 .topright .pill { display:none; }
 .hero { align-items:flex-start;flex-direction:column; }
 .metrics { gap:9px; }
 .metric { padding:14px; }
 .mvalue { font-size:23px; }
 .card { padding:16px; }
 .riskwrap { align-items:flex-start; }
 .gauge { width:95px;height:95px; }
}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
 <div class="brand">
  <div class="logo">⌁</div>
  <div class="brandtext"><h2>THREATLENS</h2><small>SECURITY INTELLIGENCE</small></div>
 </div>
 <div class="navtitle">WORKSPACE</div>
 <div class="nav active"><span class="ico">▦</span><span class="navtext">Security overview</span></div>
 <div class="nav"><span class="ico">⌕</span><span class="navtext">Document scanner</span></div>
 <div class="nav"><span class="ico">◈</span><span class="navtext">Threat findings</span></div>
 <div class="nav"><span class="ico">◷</span><span class="navtext">Scan activity</span></div>
 <div class="navtitle">SYSTEM</div>
 <div class="nav"><span class="ico">⚙</span><span class="navtext">Detection rules</span></div>
 <div class="sidebottom">
  <div class="connection"><span class="dot"></span><span style="font-size:11px">Scanner online</span>
   <p>Pattern engine active<br>Local document analysis</p></div>
 </div>
</aside>

<main>
 <div class="topbar">
  <div><div class="eyebrow">THREAT INTELLIGENCE / 01</div><h1>Security Operations Center</h1></div>
  <div class="topright"><span class="pill">LOCAL SCANNER</span><span class="pill"><span class="dot"></span>System ready</span></div>
 </div>

 <section class="hero">
  <div><div class="eyebrow">DOCUMENT DEFENSE SYSTEM</div>
   <h2>See the threat. <span>Stop the risk.</span></h2>
   <p>Inspect documents for suspicious instructions, possible prompt injection patterns, and risky data-handling language.</p>
  </div>
  <div class="badge">● PATTERN ENGINE ACTIVE</div>
 </section>

 {% if error %}<div class="alert">{{ error }}</div>{% endif %}

 <section class="metrics">
  <div class="metric"><div class="mlabel">CURRENT FILE</div><div class="mvalue" style="font-size:19px">{{ filename if filename else "—" }}</div><div class="mnote">Selected document</div></div>
  <div class="metric"><div class="mlabel">RISK SCORE</div><div class="mvalue">{{ score }}<span style="font-size:13px;color:var(--muted)"> /100</span></div><div class="mnote">Rule-based estimate</div></div>
  <div class="metric"><div class="mlabel">PATTERNS MATCHED</div><div class="mvalue">{{ findings|length }}</div><div class="mnote">Matching rule occurrences</div></div>
  <div class="metric"><div class="mlabel">SCAN STATUS</div><div class="mvalue" style="font-size:19px">{{ status }}</div><div class="mnote">{{ scanned_at if scanned_at else "Awaiting document" }}</div></div>
 </section>

 <div class="contentgrid">
  <div>
   <section class="card">
    <div class="cardhead"><div><h3>◈ &nbsp; Document inspection</h3><div class="sub">Upload a text document for local pattern analysis.</div></div><span class="tag">SCAN INPUT</span></div>
    <form method="POST" enctype="multipart/form-data" id="scanform">
     <label class="drop" id="drop">
      <div class="uploadicon">⇧</div>
      <strong>Drop your document here</strong>
      <p>or <b>browse files</b> to select a document<br>TXT format · Maximum 195 KiB</p>
      <input type="file" name="document" id="file" accept=".txt,text/plain" required>
      <div class="fileinfo" id="fileinfo"></div>
     </label>
     <button class="btn full" id="scanbtn" type="submit">⌁ &nbsp; ANALYZE DOCUMENT</button>
     <div class="scanline hidden" id="progress"><span></span></div>
    </form>
    <div class="smallnote">Files are analyzed by this Flask app. Current version supports TXT files only; it does not execute uploaded content.</div>
   </section>

   <section class="card">
    <div class="cardhead"><div><h3>◈ &nbsp; Threat findings</h3><div class="sub">Rule matches with location and surrounding context.</div></div><span class="tag">{{ findings|length }} FOUND</span></div>
    {% if findings %}
     {% for f in findings %}
      <div class="finding">
       <div class="fhead"><strong>{{ f.name }}</strong><span class="sev {{ f.severity }}">{{ f.severity }}</span></div>
       <div class="fmeta">LINE {{ f.line }} &nbsp; / &nbsp; RULE MATCH</div>
       <div class="matched">{{ f.matched_text }}</div>
       <div class="context">{{ f.context }}</div>
      </div>
     {% endfor %}
    {% else %}
     <div class="empty"><strong>◇ &nbsp; No matched patterns</strong>
      {% if status == "SCANNED" %}No current rule matched the document. This is not proof that the document is safe.{% else %}Upload a TXT file to begin scanning and populate this panel.{% endif %}
     </div>
    {% endif %}
   </section>
  </div>

  <div>
   <section class="card">
    <div class="cardhead"><div><h3>◎ &nbsp; Risk assessment</h3><div class="sub">Summary of the current scan.</div></div><span class="tag">ANALYTICS</span></div>
    <div class="riskwrap">
     <div class="gauge" style="--score:{{ score }}"><div class="gaugeinner"><strong>{{ score }}</strong><small>RISK SCORE</small></div></div>
     <div><div class="risklabel {{ risk_class }}">{{ risk }}</div><div class="resultmessage">{{ summary }}</div></div>
    </div>
    <div class="resultstats">
     <div class="rstat"><strong style="color:var(--red)">{{ high_count }}</strong><span>HIGH</span></div>
     <div class="rstat"><strong style="color:var(--yellow)">{{ medium_count }}</strong><span>MEDIUM</span></div>
     <div class="rstat"><strong style="color:var(--cyan)">{{ low_count }}</strong><span>LOW</span></div>
    </div>
   </section>

   <section class="card">
    <div class="cardhead"><div><h3>⌘ &nbsp; Recommended action</h3><div class="sub">Suggested next step from rule matches.</div></div></div>
    <div class="finding">
     <div class="fhead"><strong>{{ action_title }}</strong><span class="dot"></span></div>
     <div class="sub">{{ action_text }}</div>
    </div>
   </section>

   <section class="card">
    <div class="cardhead"><div><h3>⌬ &nbsp; Detection engine</h3><div class="sub">Current analysis capabilities</div></div></div>
    <div class="finding"><div class="fhead"><strong>Instruction override</strong><span class="tag">RULE 01</span></div></div>
    <div class="finding"><div class="fhead"><strong>Secret disclosure</strong><span class="tag">RULE 02</span></div></div>
    <div class="finding"><div class="fhead"><strong>Security bypass</strong><span class="tag">RULE 03</span></div></div>
    <div class="finding"><div class="fhead"><strong>Data handling</strong><span class="tag">RULE 04+</span></div></div>
    <div class="smallnote">Rule-based detection can miss reworded or context-dependent attacks and can flag harmless text.</div>
   </section>
  </div>
 </div>
 <div class="footer">THREATLENS // DOCUMENT SECURITY INTELLIGENCE // PROTOTYPE BUILD</div>
</main>
</div>
<script>
const input = document.getElementById("file");
const info = document.getElementById("fileinfo");
const drop = document.getElementById("drop");
const form = document.getElementById("scanform");
const btn = document.getElementById("scanbtn");
const progress = document.getElementById("progress");

input.addEventListener("change", () => {
 const f = input.files[0];
 info.textContent = f ? "▣  " + f.name + "  ·  " + (f.size / 1024).toFixed(1) + " KB" : "";
});

["dragenter","dragover"].forEach(e => drop.addEventListener(e, event => {
 event.preventDefault(); drop.classList.add("drag");
}));
["dragleave","drop"].forEach(e => drop.addEventListener(e, event => {
 event.preventDefault(); drop.classList.remove("drag");
}));
drop.addEventListener("drop", event => {
 const files = event.dataTransfer.files;
 if (files.length) {
  input.files = files;
  input.dispatchEvent(new Event("change"));
 }
});
form.addEventListener("submit", event => {
 if (!input.files.length) return;
 btn.disabled = true;
 btn.textContent = "ANALYZING DOCUMENT...";
 progress.classList.remove("hidden");
});
</script>
</body>
</html>
"""


def scan_text(text):
    findings = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        for name, pattern, severity, points in RULES:
            for match in re.finditer(pattern, line, re.IGNORECASE):
                findings.append({
                    "name": name,
                    "severity": severity,
                    "points": points,
                    "line": line_number,
                    "matched_text": match.group(0),
                    "context": line.strip()[:500]
                })

    return findings


def calculate_risk(findings):
    # Cap the score at 100; this is a demo heuristic, not a probability.
    score = min(100, sum(item["points"] for item in findings))

    if any(f["severity"] == "HIGH" for f in findings):
        risk = "HIGH"
    elif any(f["severity"] == "MEDIUM" for f in findings):
        risk = "MEDIUM"
    elif findings:
        risk = "LOW"
    else:
        risk = "SAFE"

    return risk, score


@app.route("/", methods=["GET", "POST"])
def home():
    findings = []
    filename = ""
    score = 0
    risk = "SAFE"
    status = "AWAITING SCAN"
    scanned_at = ""
    error = ""
    high_count = medium_count = low_count = 0

    summary = "Upload a document to assess its matching patterns."
    action_title = "Awaiting document"
    action_text = "Choose a TXT file to start the scan."

    if request.method == "POST":
        file = request.files.get("document")

        if not file or not file.filename:
            error = "Select a TXT file before scanning."
        elif not file.filename.lower().endswith(".txt"):
            error = "Unsupported file type. This prototype accepts TXT files only."
        else:
            filename = secure_filename(file.filename) or "document.txt"
            raw = file.stream.read(200001)

            if len(raw) > 200000:
                error = "File is too large. Maximum supported size is 200,000 bytes."
            else:
                try:
                    text = raw.decode("utf-8-sig")
                except UnicodeDecodeError:
                    text = raw.decode("utf-8", errors="replace")

                findings = scan_text(text)
                risk, score = calculate_risk(findings)
                status = "SCANNED"
                scanned_at = datetime.now().strftime("%d %b %Y · %H:%M")

                high_count = sum(f["severity"] == "HIGH" for f in findings)
                medium_count = sum(f["severity"] == "MEDIUM" for f in findings)
                low_count = sum(f["severity"] == "LOW" for f in findings)

                if risk == "HIGH":
                    summary = "High-priority rule matches require manual review."
                    action_title = "Hold for review"
                    action_text = "Do not automatically trust or ingest this file. Review each finding and its surrounding context."
                elif risk == "MEDIUM":
                    summary = "Potentially suspicious language was detected."
                    action_title = "Review findings"
                    action_text = "Check whether the matched instructions are expected in this document."
                elif findings:
                    summary = "A low-priority pattern matched."
                    action_title = "Inspect context"
                    action_text = "Confirm whether the match is relevant before deciding what to do."
                else:
                    summary = "No current detection rule matched this document."
                    action_title = "No rule match"
                    action_text = "This result is not a safety guarantee. Use other validation and security checks as appropriate."

    return render_template_string(
        HTML,
        findings=findings,
        filename=filename,
        score=score,
        risk=risk,
        risk_class=risk,
        status=status,
        scanned_at=scanned_at,
        error=error,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        summary=summary,
        action_title=action_title,
        action_text=action_text
    )


@app.errorhandler(413)
def too_large(error):
    return render_template_string(
        HTML,
        findings=[],
        filename="",
        score=0,
        risk="UNKNOWN",
        risk_class="HIGH",
        status="REJECTED",
        scanned_at="",
        error="Upload rejected: maximum file size is 200,000 bytes.",
        high_count=0,
        medium_count=0,
        low_count=0,
        summary="The uploaded file exceeded the size limit.",
        action_title="Choose a smaller file",
        action_text="Upload a TXT file smaller than 200,000 bytes."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)

RULES = [
    # 1. Instruction override
    ("Instruction Override",
     r"ignore\s+(all\s+)?(previous|prior|earlier|above)\s+(instructions|rules|directions)",
     "HIGH", 30),
    ("Instruction Override",
     r"disregard\s+(all\s+)?(previous|prior|earlier|above)\s+(instructions|rules|directions)",
     "HIGH", 30),
    ("Instruction Override",
     r"forget\s+(all\s+)?(previous|prior|earlier)\s+(instructions|rules|directions)",
     "HIGH", 30),
    ("Instruction Override",
     r"(override|replace|cancel)\s+(the\s+)?(original|system|previous|current)\s+(instructions|rules|task)",
     "HIGH", 30),
    ("Instruction Override",
     r"(your original task no longer applies|follow these instructions instead|ignore the rules above)",
     "HIGH", 30),
    ("Instruction Override",
     r"from now on.{0,40}(follow|obey|ignore|disregard)",
     "HIGH", 30),

    # 2. System prompt and secret disclosure
    ("System Prompt Disclosure",
     r"(reveal|show|print|expose|display|repeat|extract).{0,60}(system prompt|hidden instructions|internal prompt)",
     "HIGH", 30),
    ("System Prompt Disclosure",
     r"what are your (hidden|secret|system) instructions",
     "HIGH", 30),
    ("System Prompt Disclosure",
     r"(reveal|disclose|expose|print).{0,40}(password|secret|api key|access token|credentials)",
     "HIGH", 30),
    ("System Prompt Disclosure",
     r"(dump|output|list).{0,40}(environment variables|secret keys|credentials)",
     "HIGH", 30),

    # 3. Security bypass
    ("Security Bypass",
     r"(bypass|disable|evade|skip|circumvent).{0,50}(security|safety|authentication|authorization|access control)",
     "HIGH", 25),
    ("Security Bypass",
     r"(turn off|remove|ignore|override).{0,40}(security checks|safety rules|security controls|restrictions)",
     "HIGH", 25),
    ("Security Bypass",
     r"(execute|proceed|continue).{0,40}(without|despite).{0,30}(permission|authorization|approval)",
     "HIGH", 25),
    ("Security Bypass",
     r"(disable|remove|deactivate).{0,40}(safeguards|security policy|safety filters)",
     "HIGH", 25),

    # 4. Confidential data transfer
    ("Confidential Data Transfer",
     r"(send|share|transfer|upload|forward|export).{0,60}(confidential|private|sensitive|personal).{0,30}(data|information|files|records)",
     "HIGH", 25),
    ("Confidential Data Transfer",
     r"(send|upload|forward|transfer).{0,50}(all user data|customer records|private records|internal documents)",
     "HIGH", 25),
    ("Confidential Data Transfer",
     r"(transmit|share|email).{0,50}(secret information|confidential files|sensitive records)",
     "HIGH", 25),

    # 5. Role manipulation and fake authority
    ("Role Manipulation",
     r"(act as|pretend to be|you are now|roleplay as).{0,50}(admin|administrator|developer|system|root|unrestricted)",
     "MEDIUM", 15),
    ("Role Manipulation",
     r"(developer mode|admin mode|unrestricted mode).{0,30}(enabled|activated|on)",
     "MEDIUM", 15),
    ("Role Manipulation",
     r"(I am|this is).{0,30}(the administrator|your developer|the system administrator)",
     "MEDIUM", 15),
    ("Role Manipulation",
     r"(you have|you now have).{0,40}(administrator|root|elevated) (access|privileges|permissions)",
     "MEDIUM", 15),

    # 6. Instruction concealment
    ("Instruction Concealment",
     r"(do not tell|don't tell|hide this from|keep this secret from).{0,50}(user|owner|reviewer|administrator)",
     "MEDIUM", 15),
    ("Instruction Concealment",
     r"(do not mention|never mention|conceal|hide).{0,40}(this instruction|this action|this activity)",
     "MEDIUM", 15),
    ("Instruction Concealment",
     r"(pretend|claim|say) that (you did not|nothing).{0,30}(happen|change|occur)",
     "MEDIUM", 15),

    # 7. Data exfiltration
    ("Data Exfiltration",
     r"(extract|dump|exfiltrate|harvest|collect).{0,50}(data|records|credentials|passwords|tokens)",
     "HIGH", 25),
    ("Data Exfiltration",
     r"(copy|retrieve|download).{0,50}(all|private|confidential|sensitive).{0,30}(data|records|files)",
     "HIGH", 25),
    ("Data Exfiltration",
     r"(send|post|upload).{0,50}(data|results|records).{0,40}(external server|external website|remote server)",
     "HIGH", 25),

    # 8. Audit and log evasion
    ("Audit Evasion",
     r"(delete|erase|clear|remove).{0,40}(audit logs|security logs|activity logs|logs)",
     "HIGH", 25),
    ("Audit Evasion",
     r"(avoid|prevent|disable).{0,40}(logging|audit trail|monitoring|detection)",
     "MEDIUM", 15),
    ("Audit Evasion",
     r"(leave no trace|avoid detection|cover your tracks|conceal the activity)",
     "MEDIUM", 15),

    # 9. Prompt injection through indirect instructions
    ("Indirect Prompt Injection",
     r"(when you read this|if an ai reads this|to any ai assistant).{0,60}(ignore|override|reveal|send|execute)",
     "HIGH", 25),
    ("Indirect Prompt Injection",
     r"(assistant|ai model|language model).{0,40}(must ignore|should ignore|must reveal|must disclose)",
     "HIGH", 25),
    ("Indirect Prompt Injection",
     r"(this document|this message|these notes).{0,50}(override|replace|supersede).{0,30}(instructions|system prompt|rules)",
     "HIGH", 25),


