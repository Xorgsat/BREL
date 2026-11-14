"""
Controlled Local Test Application for BREL (FastAPI).
Provides deterministic, seedable, microsecond-accurate browser scenarios
to isolate automation mechanics from third-party network jitter.
"""

from __future__ import annotations

import asyncio
import random
from typing import Optional

from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="BREL Controlled Reliability Testbed", version="1.0.0")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "BREL Controlled Testbed"}


@app.get("/", response_class=HTMLResponse)
async def home():
    return """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BREL Controlled Testbed</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; }
            h1 { color: #1a365d; }
            ul { line-height: 1.8; }
            a { color: #2b6cb0; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; }
            .badge { background: #edf2f7; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }
        </style>
    </head>
    <body>
        <h1>Browser Reliability Engineering Lab (BREL) — Controlled Testbed</h1>
        <p>Deterministic local test application for synchronization, flakiness, and lifecycle experiments.</p>
        <ul>
            <li><a href="/scenarios/dynamic-render?delay_ms=1000">Dynamic Render Scenario</a> <span class="badge">EXP-01, EXP-02</span></li>
            <li><a href="/scenarios/stale-dom?recycle_ms=500">Stale DOM Lifecycle Scenario</a> <span class="badge">EXP-03</span></li>
            <li><a href="/scenarios/click-interception?overlay_ms=1500">Click Interception & Overlay Scenario</a> <span class="badge">EXP-04</span></li>
            <li><a href="/scenarios/race-condition?race_window_ms=200">Async Race Condition Scenario</a> <span class="badge">EXP-13</span></li>
            <li><a href="/scenarios/shadow-dom">Shadow DOM Web Components</a> <span class="badge">EXP-06</span></li>
            <li><a href="/scenarios/frames">Nested Frames Scenario</a> <span class="badge">EXP-05</span></li>
        </ul>
    </body>
    </html>
    """


@app.get("/scenarios/dynamic-render", response_class=HTMLResponse)
async def dynamic_render(delay_ms: int = Query(default=1000)):
    return f"""<!DOCTYPE html>
    <html>
    <head><title>Dynamic Render Test</title></head>
    <body>
        <h2>Dynamic Render Experiment</h2>
        <button id="trigger-btn" onclick="startRender()">Load Element</button>
        <div id="container" style="margin-top: 20px;"></div>
        <script>
            function startRender() {{
                const btn = document.getElementById('trigger-btn');
                btn.disabled = true;
                btn.innerText = 'Loading...';
                setTimeout(() => {{
                    const el = document.createElement('div');
                    el.id = 'target-element';
                    el.className = 'rendered-card';
                    el.innerText = 'Target Loaded Successfully!';
                    document.getElementById('container').appendChild(el);
                    btn.innerText = 'Completed';
                }}, {delay_ms});
            }}
        </script>
    </body>
    </html>
    """


@app.get("/scenarios/stale-dom", response_class=HTMLResponse)
async def stale_dom(recycle_ms: int = Query(default=500)):
    return f"""<!DOCTYPE html>
    <html>
    <head><title>Stale DOM Test</title></head>
    <body>
        <h2>Stale DOM Invalidation Experiment</h2>
        <div id="parent-container">
            <button id="victim-element" class="btn" onclick="mutateDOM()">Click To Recycle DOM</button>
        </div>
        <div id="status-log">Initial State</div>
        <script>
            function mutateDOM() {{
                const log = document.getElementById('status-log');
                log.innerText = 'Recycling DOM node in {recycle_ms}ms...';
                setTimeout(() => {{
                    const parent = document.getElementById('parent-container');
                    parent.innerHTML = '<button id="victim-element" class="btn recycled">Recycled Button Node</button>';
                    log.innerText = 'Node successfully replaced in DOM';
                }}, {recycle_ms});
            }}
        </script>
    </body>
    </html>
    """


@app.get("/scenarios/click-interception", response_class=HTMLResponse)
async def click_interception(overlay_ms: int = Query(default=1500)):
    return f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Click Interception Test</title>
        <style>
            #blocking-overlay {{
                position: fixed;
                top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0, 0, 255, 0.4);
                display: flex; align-items: center; justify-content: center;
                color: white; font-size: 24px; z-index: 9999;
            }}
            .hidden {{ display: none !important; }}
        </style>
    </head>
    <body>
        <h2>Click Interception Experiment</h2>
        <div id="blocking-overlay">Loading Backdrop (Blocks User Input)</div>
        <button id="target-action-btn" onclick="registerClick()">Submit Order</button>
        <div id="click-feedback" style="margin-top: 15px;">Awaiting Click</div>
        <script>
            function registerClick() {{
                document.getElementById('click-feedback').innerText = 'Action Button Successfully Clicked!';
            }}
            // Decay overlay after overlay_ms
            setTimeout(() => {{
                const overlay = document.getElementById('blocking-overlay');
                if (overlay) {{
                    overlay.classList.add('hidden');
                }}
            }}, {overlay_ms});
        </script>
    </body>
    </html>
    """


@app.get("/scenarios/race-condition", response_class=HTMLResponse)
async def race_condition(race_window_ms: int = Query(default=100)):
    return f"""<!DOCTYPE html>
    <html>
    <head><title>Race Condition Test</title></head>
    <body>
        <h2>Asynchronous Race Condition Experiment</h2>
        <button id="race-trigger-btn" onclick="triggerRace()">Submit Token</button>
        <div id="race-status">Ready</div>
        <div id="final-state">NONE</div>
        <script>
            let listenerAttached = false;
            // Deliberately delay event handler binding or state commitment
            setTimeout(() => {{
                listenerAttached = true;
            }}, {race_window_ms});

            function triggerRace() {{
                if (!listenerAttached) {{
                    document.getElementById('race-status').innerText = 'RACE_LOST_CLICK_IGNORED';
                    document.getElementById('final-state').innerText = 'FAILED_EARLY_INTERACTION';
                }} else {{
                    document.getElementById('race-status').innerText = 'RACE_WON_STATE_COMMITTED';
                    document.getElementById('final-state').innerText = 'SUCCESS_TOKEN_ACCEPTED';
                }}
            }}
        </script>
    </body>
    </html>
    """


@app.get("/scenarios/shadow-dom", response_class=HTMLResponse)
async def shadow_dom():
    return """<!DOCTYPE html>
    <html>
    <head><title>Shadow DOM Test</title></head>
    <body>
        <h2>Shadow DOM Encapsulation Experiment</h2>
        <div id="shadow-host"></div>
        <script>
            const host = document.getElementById('shadow-host');
            const shadowRoot = host.attachShadow({mode: 'open'});
            shadowRoot.innerHTML = `
                <style>
                    .shadow-box { padding: 15px; border: 2px solid #3182ce; border-radius: 6px; }
                    .shadow-text { color: #2c5282; font-weight: bold; }
                </style>
                <div class="shadow-box">
                    <p class="shadow-text" id="shadow-content">Inside Open Shadow Root</p>
                    <button id="shadow-btn" onclick="alert('Shadow Clicked')">Shadow Action</button>
                </div>
            `;
        </script>
    </body>
    </html>
    """


@app.get("/scenarios/frames", response_class=HTMLResponse)
async def frames():
    return """<!DOCTYPE html>
    <html>
    <head><title>Frames Test</title></head>
    <body>
        <h2>Nested Frame Isolation Experiment</h2>
        <iframe id="child-frame" srcdoc="
            <html>
                <body style='background: #faf5ff;'>
                    <h3 id='frame-heading'>Inside Child Frame Document</h3>
                    <button id='frame-action-btn' onclick='this.innerText=\"Clicked in Frame\"'>Click Inside Frame</button>
                </body>
            </html>
        " width="500" height="250"></iframe>
    </body>
    </html>
    """


@app.get("/api/data")
async def delayed_api(
    delay_ms: int = Query(default=1000),
    failure_rate: float = Query(default=0.0),
    seed: Optional[int] = Query(default=None),
):
    if seed is not None:
        random.seed(seed)
    if delay_ms > 0:
        await asyncio.sleep(delay_ms / 1000.0)
    if failure_rate > 0 and random.random() < failure_rate:
        return JSONResponse(status_code=500, content={"error": "Injected Network Failure"})
    return {"status": "success", "data": "payload_verified", "delay_ms": delay_ms}
