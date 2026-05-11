# Securo — Vulnerability Scanner

## What it does
Securo is a web-based static code security analysis platform. Users submit code (paste, GitHub/GitLab URL, or file upload), and Securo runs Semgrep with OWASP Top 10 rules across 30+ languages, returns a detailed vulnerability report with file paths, line numbers, severity levels, and code snippets. A Gemini 2.5 AI assistant then explains vulnerabilities and suggests fixes.

## Who uses it
Developers and security engineers who want fast, free vulnerability scanning without setting up local tooling. Target: individual devs, small teams, students learning secure coding.

## Core screens
- **Landing** — hero, features grid (6 cards), how-it-works steps (4), CTA
- **Scan** — input form with 3 modes: code paste / repo URL / file upload
- **Results** — vulnerability cards with severity filter, stats, AI assistant chat overlay
- **History** — table of past scans with export to JSON
- **Profile** — account stats, scan counts by severity

## Brand voice
Precise, technical, no-nonsense. Tool for professionals. Confident but not aggressive. Terminal/hacker aesthetic without being a toy.

## Visual identity
- **Mode:** CRT Terminal / Tactical Telemetry (dark mode only)
- **Palette:** Pure black `#000000` bg, `#00ff41` phosphor green accent, white text, `#ff3333` danger, `#ff9500` warning
- **Typography:** JetBrains Mono monospace — intentional, consistent with terminal aesthetic
- **Motifs:** scanlines, ASCII brackets `[SECURO]`, `>` prompt prefix, `//` section markers, cursor blink
- **Feel:** Declassified military database meets modern SaaS. Serious tool that happens to look exceptional.

## Design constraints
- No build tool (vanilla CSS + vanilla JS + Jinja2 templates)
- GSAP 3.12 available via CDN for animations
- Must stay monospace — single-font is a deliberate aesthetic choice, not a bug
- No external UI frameworks (no Tailwind, no Bootstrap)
- Flask/Python backend — templates are Jinja2
