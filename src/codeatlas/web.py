"""Minimal web interface for the initial CodeAtlas milestone.

Bind to 127.0.0.1; add authentication and path access policy before public deployment.
"""
from __future__ import annotations

import subprocess

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .analyzer import analyze
from .source import snapshot

app = FastAPI(title="CodeAtlas", version="0.1.0")


class ScanRequest(BaseModel):
    source: str


@app.post("/api/analyse")
def analyse(request: ScanRequest):
    try:
        with snapshot(request.source) as root:
            return analyze(root)
    except (ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        raise HTTPException(status_code=400, detail=f"Analysis failed: {type(exc).__name__}") from exc


@app.get("/", response_class=HTMLResponse)
def home():
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CodeAtlas</title><style>
body{font-family:system-ui;background:#0c1423;color:#e8efff;margin:0;padding:2rem}
main{max-width:1100px;margin:auto}input{padding:12px;width:min(680px,90%);background:#18243a;
color:white;border:1px solid #506078;border-radius:8px}
button{padding:12px 20px;background:#44cab3;color:#082321;border:0;border-radius:8px;cursor:pointer}
pre{overflow:auto;background:#18243a;padding:20px;border-radius:10px;max-height:65vh}
.summary{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}
.summary span{background:#18243a;padding:16px;border-radius:9px}
a{color:#44cab3}</style></head><body><main>
<h1>CodeAtlas</h1><p>Explore function relationships and potential orphan code in Python projects.</p>
<form id="scan"><input id="source" required placeholder="Local folder or https://github.com/owner/repo">
<button id="go">Analyse</button></form><p id="status"></p>
<section id="stats" class="summary"></section><h2>Analysis report</h2>
<p>Function and call relationships are returned as structured JSON in this first milestone.</p>
<button id="save" hidden>Download JSON</button><pre id="result">No scan yet.</pre>
<script>
let last=null;
document.getElementById('scan').addEventListener('submit',async e=>{
 e.preventDefault();const go=document.getElementById('go');go.disabled=true;
 document.getElementById('status').textContent='Scanning…';
 try{const response=await fetch('/api/analyse',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({source:document.getElementById('source').value})});
 const data=await response.json();if(!response.ok)throw Error(data.detail||'Scan failed');
 last=data;document.getElementById('status').textContent='Scan complete';
 document.getElementById('stats').replaceChildren(...Object.entries(data.summary).map(([key,value])=>{
 const s=document.createElement('span');s.textContent=key.replaceAll('_',' ')+': '+value;return s}));
 document.getElementById('result').textContent=JSON.stringify(data,null,2);
 document.getElementById('save').hidden=false;
 }catch(error){document.getElementById('status').textContent=error.message;}
 finally{go.disabled=false;}
});
document.getElementById('save').addEventListener('click',()=>{
 if(!last)return;const blob=new Blob([JSON.stringify(last,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),link=document.createElement('a');
 link.href=url;link.download='codeatlas-report.json';link.click();URL.revokeObjectURL(url);
});
</script></main></body></html>"""
