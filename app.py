

from flask import Flask, request, render_template_string
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200000

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SecureRAG | AI Security</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #0b0b12;
    --panel: #13131d;
    --panel2: #191927;
    --violet: #a78bfa;
    --bright: #c4b5fd;
    --muted: #9393a8;
    --border: rgba(196,181,253,.13);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
}

body {
    background: var(--bg);
    color: #f4f2ff;
    font-family: 'Inter', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -2;
    background:
        radial-gradient(ellipse at 15% 10%,
            rgba(139,92,246,.13), transparent 38%),
        radial-gradient(ellipse at 90% 40%,
            rgba(124,58,237,.09), transparent 35%);
}

.grid-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -1;
    opacity: .10;
    background-image:
        linear-gradient(rgba(196,181,253,.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(196,181,253,.12) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(to bottom, black, transparent 90%);
}

nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 19px 7%;
    border-bottom: 1px solid var(--border);
    background: rgba(11,11,18,.85);
    backdrop-filter: blur(18px);
    position: sticky;
    top: 0;
    z-index: 10;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 23px;
    font-weight: 700;
    letter-spacing: -1px;
}

.logo {
    display: grid;
    place-items: center;
    width: 42px;
    height: 42px;
    border-radius: 13px;
    font-size: 22px;
    background: linear-gradient(135deg, #5b21b6, #8b5cf6);
    box-shadow: 0 0 28px rgba(167,139,250,.19);
}

.brand span {
    color: var(--violet);
}

.nav-right {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #c4c0d8;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.live-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #a78bfa;
    box-shadow: 0 0 12px #a78bfa;
    animation: pulse 2s infinite;
}

main {
    max-width: 1180px;
    margin: auto;
    padding: 60px 25px 70px;
}

.hero {
    display: grid;
    grid-template-columns: 1.2fr .8fr;
    gap: 35px;
    align-items: center;
    margin-bottom: 60px;
    animation: rise .8s ease both;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 9px;
    padding: 9px 14px;
    border: 1px solid rgba(167,139,250,.25);
    border-radius: 30px;
    background: rgba(139,92,246,.08);
    color: var(--bright);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.4px;
}

h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(38px, 5vw, 60px);
    line-height: 1.09;
    letter-spacing: -2.5px;
    margin: 25px 0 20px;
}

.gradient-text {
    background: linear-gradient(100deg, #c4b5fd, #8b5cf6, #e9d5ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.hero p {
    max-width: 560px;
    color: var(--muted);
    line-height: 1.9;
    font-size: 14px;
}

.hero-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 28px;
}

.btn {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    gap: 9px;
    padding: 13px 19px;
    border-radius: 10px;
    border: 1px solid var(--border);
    color: white;
    text-decoration: none;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    font-family: inherit;
    transition: transform .25s, box-shadow .25s, background .25s;
}

.btn:hover {
    transform: translateY(-3px);
}

.btn-primary {
    background: linear-gradient(110deg, #6d28d9, #8b5cf6);
    border: 1px solid rgba(196,181,253,.3);
    box-shadow: 0 7px 28px rgba(139,92,246,.17);
}

.btn-primary:hover {
    box-shadow: 0 8px 35px rgba(139,92,246,.32);
}

.btn-secondary {
    background: rgba(255,255,255,.025);
}

.visual {
    min-height: 300px;
    position: relative;
    display: grid;
    place-items: center;
    overflow: hidden;
    border: 1px solid var(--border);
    border-radius: 25px;
    background: radial-gradient(circle at center,
        rgba(139,92,246,.13), rgba(19,19,29,.4) 70%);
}

.orbit {
    position: absolute;
    width: 245px;
    height: 245px;
    border: 1px solid rgba(167,139,250,.26);
    border-radius: 50%;
    animation: rotate 18s linear infinite;
}

.orbit.two {
    width: 185px;
    height: 185px;
    border-color: rgba(196,181,253,.35);
    animation-direction: reverse;
    animation-duration: 12s;
}

.orbit::before {
    content: "";
    position: absolute;
    top: 23px;
    left: 30px;
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #c4b5fd;
    box-shadow: 0 0 20px #a78bfa;
}

.core {
    width: 108px;
    height: 108px;
    display: grid;
    place-items: center;
    border-radius: 30px;
    font-size: 47px;
    background: linear-gradient(145deg, #292044, #4c1d95);
    border: 1px solid rgba(196,181,253,.35);
    box-shadow: 0 0 65px rgba(139,92,246,.22);
    animation: float 4s ease-in-out infinite;
}

.visual-label {
    position: absolute;
    bottom: 23px;
    color: #c2bad9;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.section-heading {
    display: flex;
    align-items: end;
    justify-content: space-between;
    gap: 15px;
    margin-bottom: 22px;
}

.section-heading h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 26px;
    letter-spacing: -.7px;
}

.section-heading p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.7;
    margin-top: 7px;
}

.tag {
    color: var(--bright);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

.panel {
    background: rgba(19,19,29,.91);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 27px;
    backdrop-filter: blur(18px);
    box-shadow: 0 18px 55px rgba(0,0,0,.15);
}

.scanner-layout {
    display: grid;
    grid-template-columns: 1fr .75fr;
    gap: 20px;
    align-items: stretch;
}

.drop-zone {
    min-height: 275px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px dashed rgba(167,139,250,.4);
    border-radius: 16px;
    background: radial-gradient(ellipse at center,
        rgba(139,92,246,.09), rgba(19,19,29,.15));
    padding: 24px;
    text-align: center;
    transition: border-color .25s, background .25s, box-shadow .25s;
}

.drop-zone:hover,
.drop-zone.dragover {
    border-color: #c4b5fd;
    background: rgba(139,92,246,.11);
    box-shadow: inset 0 0 35px rgba(139,92,246,.07);
}

.upload-icon {
    width: 65px;
    height: 65px;
    display: grid;
    place-items: center;
    border-radius: 20px;
    background: rgba(139,92,246,.13);
    border: 1px solid rgba(167,139,250,.26);
    color: #d8b4fe;
    font-size: 29px;
    margin-bottom: 19px;
    animation: float 4s ease-in-out infinite;
}

.drop-zone h3 {
    font-size: 16px;
    margin-bottom: 9px;
}

.drop-zone p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
}

.file-input {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
    overflow: hidden;
}

.choose-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin: 16px 0 10px;
    padding: 11px 17px;
    border: 1px solid rgba(167,139,250,.3);
    border-radius: 9px;
    background: rgba(139,92,246,.12);
    color: #ddd6fe;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: .2s;
}

.choose-btn:hover {
    background: rgba(139,92,246,.23);
}

#fileName {
    overflow-wrap: anywhere;
    color: #c4b5fd;
    font-size: 11px;
}

.scan-btn {
    width: 100%;
    margin-top: 13px;
}

.scan-btn:disabled {
    opacity: .7;
    cursor: wait;
}

.info-panel h3 {
    font-size: 15px;
    margin-bottom: 20px;
}

.check-row {
    display: flex;
    gap: 13px;
    padding: 15px 0;
    border-bottom: 1px solid var(--border);
}

.check-row:last-child {
    border-bottom: none;
}

.check-icon {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    background: rgba(139,92,246,.12);
    color: #c4b5fd;
}

.check-row strong {
    font-size: 12px;
}

.check-row p {
    margin-top: 5px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
}

.results {
    margin-top: 25px;
    animation: rise .5s ease both;
}

.result-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
    margin-bottom: 25px;
}

.result-top h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
}

.risk-badge {
    padding: 8px 12px;
    border-radius: 30px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
    background: rgba(74,222,128,.09);
    color: #86efac;
    border: 1px solid rgba(74,222,128,.23);
}

.risk-high {
    background: rgba(248,113,113,.09);
    color: #fca5a5;
    border-color: rgba(248,113,113,.25);
}

.risk-unknown {
    background: rgba(251,191,36,.09);
    color: #fcd34d;
    border-color: rgba(251,191,36,.25);
}

.result-grid {
    display: grid;
    grid-template-columns: 190px 1fr;
    gap: 25px;
    align-items: center;
}

.meter-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

.meter {
    position: relative;
    width: 170px;
    height: 170px;
}

.meter svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
    overflow: visible;
}

.meter-track {
    fill: none;
    stroke: #292638;
    stroke-width: 8;
}

.meter-value {
    fill: none;
    stroke: #a78bfa;
    stroke-width: 8;
    stroke-linecap: round;
    stroke-dasharray: 314.16;
    stroke-dashoffset: calc(314.16 - 314.16 * var(--score) / 100);
    filter: drop-shadow(0 0 6px rgba(167,139,250,.55));
    animation: meter-in 1.1s ease both;
}

.meter-value.high {
    stroke: #f87171;
    filter: drop-shadow(0 0 6px rgba(248,113,113,.4));
}

.meter-value.unknown {
    stroke: #fbbf24;
}

.meter-center {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.score-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 43px;
    line-height: 1.1;
    font-weight: 700;
    letter-spacing: -2px;
}

.score-caption {
    margin-top: 7px;
    font-size: 9px;
    color: var(--muted);
    letter-spacing: 2px;
}

.meter-label {
    color: var(--bright);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
}

.report-details {
    min-width: 0;
}

.report-details h4 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 21px;
    line-height: 1.4;
    margin-bottom: 8px;
    overflow-wrap: anywhere;
}

.report-details > p {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
}

.detail-row {
    display: flex;
    gap: 12px;
    align-items: flex-start;
    margin-top: 18px;
    padding: 15px;
    border: 1px solid var(--border);
    border-radius: 12px;
    background: rgba(255,255,255,.02);
}

.detail-icon {
    color: var(--bright);
    font-size: 18px;
}

.detail-row strong {
    display: block;
    font-size: 11px;
    margin-bottom: 5px;
}

.detail-row p {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.7;
    overflow-wrap: anywhere;
}

.hold-status {
    color: #fca5a5 !important;
}

.result-note {
    margin-top: 19px;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.8;
}

.features {
    margin-top: 60px;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 17px;
}

.feature-card {
    background: rgba(19,19,29,.78);
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 24px;
    transition: transform .25s, border-color .25s;
}

.feature-card:hover {
    transform: translateY(-5px);
    border-color: rgba(167,139,250,.4);
}

.feature-icon {
    width: 45px;
    height: 45px;
    display: grid;
    place-items: center;
    border-radius: 13px;
    font-size: 21px;
    color: #d8b4fe;
    background: linear-gradient(135deg,
        rgba(139,92,246,.18), rgba(167,139,250,.07));
    margin-bottom: 20px;
}

.feature-card h3 {
    font-size: 14px;
    margin-bottom: 10px;
}

.feature-card p {
    color: var(--muted);
    font-size: 11px;
    line-height: 1.9;
}

.pipeline {
    margin-top: 45px;
}

.pipeline-steps {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-top: 22px;
}

.step {
    padding: 20px 13px;
    border-radius: 13px;
    border: 1px solid var(--border);
    background: rgba(19,19,29,.75);
    text-align: center;
    transition: border-color .25s, transform .25s;
}

.step:hover {
    transform: translateY(-4px);
    border-color: rgba(167,139,250,.4);
}

.step-num {
    font-size: 10px;
    color: var(--bright);
    margin-bottom: 12px;
    font-weight: 800;
    letter-spacing: 1px;
}

.step strong {
    font-size: 12px;
}

.step p {
    font-size: 10px;
    color: var(--muted);
    margin-top: 8px;
    line-height: 1.7;
}

footer {
    border-top: 1px solid var(--border);
    padding: 26px 15px;
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    line-height: 1.9;
}

footer strong {
    color: var(--bright);
}

@keyframes pulse {
    50% { opacity: .4; }
}

@keyframes rotate {
    to { transform: rotate(360deg); }
}

@keyframes float {
    50% { transform: translateY(-8px); }
}

@keyframes rise {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes meter-in {
    from { stroke-dashoffset: 314.16; }
}

@media (max-width: 760px) {
    nav { padding: 16px 5%; }
    main { padding: 40px 18px; }
    .hero { grid-template-columns: 1fr; }
    .visual { min-height: 255px; }
    .scanner-layout { grid-template-columns: 1fr; }
    .feature-grid { grid-template-columns: 1fr; }
    .pipeline-steps { grid-template-columns: repeat(2, 1fr); }
    .result-grid { grid-template-columns: 1fr; }
    .metrics { grid-template-columns: 1fr; }
    h1 { letter-spacing: -1.5px; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
    }
}
</style>
</head>

<body>
<div class="grid-bg"></div>

<nav>
    <div class="brand">
        <div class="logo">⬡</div>
        Secure<span>RAG</span>
    </div>
    <div class="nav-right">
        <span class="live-dot"></span>
        AI SECURITY CONSOLE
    </div>
</nav>

<main>
    <section class="hero">
        <div>
            <div class="eyebrow">✦ &nbsp; AI DOCUMENT DEFENSE</div>
            <h1>
                Trust your data.<br>
                <span class="gradient-text">Verify every document.</span>
            </h1>
            <p>
                Inspect documents before they enter your
                Retrieval-Augmented Generation knowledge pipeline.
                Identify known suspicious instructions and flag
                potentially unsafe content for review.
            </p>
            <div class="hero-buttons">
                <a class="btn btn-primary" href="#scanner">
                    ⌕ &nbsp; Start Security Scan
                </a>
                <a class="btn btn-secondary" href="#pipeline">
                    Explore workflow ↗
                </a>
            </div>
        </div>

        <div class="visual">
            <div class="orbit"></div>
            <div class="orbit two"></div>
            <div class="core">🛡️</div>
            <div class="visual-label">Document Defense System</div>
        </div>
    </section>

    <section id="scanner">
        <div class="section-heading">
            <div>
                <h2>Document Scanner</h2>
                <p>Analyze a TXT document for known suspicious phrases.</p>
            </div>
            <span class="tag">01 / ANALYZE</span>
        </div>

        <div class="scanner-layout">
            <div class="panel">
                <form method="POST" enctype="multipart/form-data" id="scanForm">
                    <div class="drop-zone" id="dropZone">
                        <div class="upload-icon">⇧</div>
                        <h3>Drop your document here</h3>
                        <p>Or browse your computer to select a TXT file</p>
                        <p>Maximum file size: 200 KB</p>

                        <input class="file-input" type="file"
                               name="document" id="document"
                               accept=".txt,text/plain" required>

                        <label class="choose-btn" for="document">
                            Choose document ↗
                        </label>

                        <p id="fileName">No document selected</p>
                    </div>

                    <button class="btn btn-primary scan-btn"
                            type="submit" id="scanButton">
                        ⌕ &nbsp; Analyze Document
                    </button>
                </form>
            </div>

            <div class="panel info-panel">
                <h3>Security inspection</h3>

                <div class="check-row">
                    <div class="check-icon">⌘</div>
                    <div>
                        <strong>Prompt Injection</strong>
                        <p>Checks for selected phrases that attempt
                           to override instructions or reveal sensitive prompts.</p>
                    </div>
                </div>

                <div class="check-row">
                    <div class="check-icon">◈</div>
                    <div>
                        <strong>Risk Assessment</strong>
                        <p>Assigns a prototype risk score based on
                           matching detection rules.</p>
                    </div>
                </div>

                <div class="check-row">
                    <div class="check-icon">⬡</div>
                    <div>
                        <strong>Threat Isolation</strong>
                        <p>Recommends an ingestion hold when a
                           suspicious phrase is detected.</p>
                    </div>
                </div>
            </div>
        </div>

        {% if result %}
        <div class="panel results" id="results">
            <div class="result-top">
                <h3>✦ Security Assessment</h3>
                <span class="risk-badge
                    {{ 'risk-high' if risk == 'High' else
                       'risk-unknown' if risk == 'Unknown' else '' }}">
                    {{ risk | e }} RISK
                </span>
            </div>

            <div class="result-grid">
                <div class="meter-wrap">
                    <div class="meter">
                        <svg viewBox="0 0 120 120" role="img"
                             aria-label="Risk score meter">
                            <circle class="meter-track"
                                    cx="60" cy="60" r="50"/>
                            <circle class="meter-value
                                {{ 'high' if risk == 'High' else
                                   'unknown' if risk == 'Unknown' else '' }}"
                                    cx="60" cy="60" r="50"
                                    style="--score: {{ score }}"/>
                        </svg>
                        <div class="meter-center">
                            <div class="score-number">{{ score }}</div>
                            <div class="score-caption">RISK SCORE</div>
                        </div>
                    </div>
                    <div class="meter-label">OUT OF 100</div>
                </div>

                <div class="report-details">
                    <h4>{{ category | e }}</h4>
                    <p>{{ result | e }}</p>

                    <div class="detail-row">
                        <div class="detail-icon">◈</div>
                        <div>
                            <strong>DOCUMENT STATUS</strong>
                            <p class="hold-status">
                                {{ 'INGESTION HOLD — RECOMMENDED'
                                   if risk == 'High'
                                   else 'ADDITIONAL CHECKS REQUIRED'
                                   if risk == 'Low'
                                   else 'MANUAL CHECK REQUIRED' }}
                            </p>
                        </div>
                    </div>

                    <div class="detail-row">
                        <div class="detail-icon">⛨</div>
                        <div>
                            <strong>RECOMMENDED OPERATION: THREAT ISOLATION</strong>
                            <p>{{ action | e }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <p class="result-note">
                Document: {{ filename | e }}<br>
                This prototype recommends an ingestion hold but does not
                physically isolate documents or block a vector database.
                A low score does not guarantee that a document is safe.
            </p>
        </div>
        {% endif %}
    </section>

    <section class="features">
        <div class="section-heading">
            <div>
                <h2>Designed for safer AI retrieval</h2>
                <p>The core ideas behind the SecureRAG project.</p>
            </div>
            <span class="tag">02 / PROTECT</span>
        </div>

        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">⌕</div>
                <h3>Detect suspicious content</h3>
                <p>Inspect incoming text for known prompt-injection
                   patterns before considering it for ingestion.</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">⛨</div>
                <h3>Hold before ingestion</h3>
                <p>Recommend holding flagged documents for review
                   before they enter trusted knowledge sources.</p>
            </div>

            <div class="feature-card">
                <div class="feature-icon">⟡</div>
                <h3>Build a secure pipeline</h3>
                <p>Prepare for future content sanitization,
                   embedding checks, and controlled vector storage.</p>
            </div>
        </div>
    </section>

    <section class="pipeline" id="pipeline">
        <div class="section-heading">
            <div>
                <h2>The SecureRAG workflow</h2>
                <p>Planned stages of a safer document-ingestion system.</p>
            </div>
            <span class="tag">03 / PIPELINE</span>
        </div>

        <div class="pipeline-steps">
            <div class="step">
                <div class="step-num">STEP 01</div>
                <strong>Document Input</strong>
                <p>Receive a document for inspection.</p>
            </div>
            <div class="step">
                <div class="step-num">STEP 02</div>
                <strong>Threat Analysis</strong>
                <p>Inspect for known suspicious patterns.</p>
            </div>
            <div class="step">
                <div class="step-num">STEP 03</div>
                <strong>Threat Isolation</strong>
                <p>Recommend an ingestion hold and human review.</p>
            </div>
            <div class="step">
                <div class="step-num">STEP 04</div>
                <strong>Secure Storage</strong>
                <p>Future integration with embeddings and vector storage.</p>
            </div>
        </div>
    </section>
</main>

<footer>
    <strong>SecureRAG</strong> · CYBERGEN 2026 Hackathon Prototype<br>
    Document security for Retrieval-Augmented Generation systems.
</footer>

<script>
const fileInput = document.getElementById("document");
const fileName = document.getElementById("fileName");
const dropZone = document.getElementById("dropZone");
const scanForm = document.getElementById("scanForm");
const scanButton = document.getElementById("scanButton");

fileInput.addEventListener("change", function () {
    if (this.files.length) {
        fileName.textContent = "Selected: " + this.files[0].name;
    } else {
        fileName.textContent = "No document selected";
    }
});

dropZone.addEventListener("dragover", function (event) {
    event.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", function () {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", function (event) {
    event.preventDefault();
    dropZone.classList.remove("dragover");

    const files = event.dataTransfer.files;
    if (files.length && files[0].name.toLowerCase().endsWith(".txt")) {
        const transfer = new DataTransfer();
        transfer.items.add(files[0]);
        fileInput.files = transfer.files;
        fileName.textContent = "Selected: " + files[0].name;
    } else {
        fileName.textContent = "Please choose a TXT file.";
    }
});

scanForm.addEventListener("submit", function () {
    scanButton.textContent = "⟳  Analyzing document...";
    scanButton.disabled = true;
});
</script>
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
            text = file.read(200000).decode(
                "utf-8", errors="replace"
            )

            patterns = [
                r"ignore (all )?(previous|prior) instructions",
                r"reveal (the )?(system prompt|passwords)",
                r"send .* confidential data",
                r"bypass (security|safety)"
            ]

            found = any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in patterns
            )

            if found:
                risk = "High"
                score = 80
                category = "Indirect Prompt Injection"
                result = "A suspicious instruction matched a detection rule."
                action = "Hold document for security review"
            else:
                risk = "Low"
                score = 0
                category = "No known pattern matched"
                result = "No matching suspicious phrase was found."
                action = "Run additional security checks before ingestion"

    return render_template_string(
        HTML,
        result=result,
        filename=filename,
        risk=risk,
        score=score,
        category=category,
        action=action
    )


@app.errorhandler(413)
def file_too_large(error):
    return (
        "File too large. Please upload a TXT document under 200 KB.",
        413
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
