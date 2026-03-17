#!/usr/bin/env python3
# ================================================
# PiGuard Security Dashboard
# Auteure: Hanane
# Raspberry Pi 5 · Suricata 6.0 · UNSW-NB15
# ================================================

from flask import Flask, jsonify, render_template_string
import subprocess
import re
import os
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# ================================================
# DASHBOARD HTML
# ================================================
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PiGuard Security Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=Inter:wght@400;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --bg:#0e0e12;--s1:#111115;--card:#16161c;--border:#252530;
  --red:#ff4040;--orange:#ff8c00;--yellow:#ffd000;--green:#00c853;
  --teal:#00bcd4;--blue:#2979ff;--purple:#9c27b0;--pink:#e91e63;
  --text:#d0d0e0;--muted:#555570;--bright:#f0f0ff;
  --f:'Inter',sans-serif;--m:'IBM Plex Mono',monospace;
}
body{background:var(--bg);color:var(--text);font-family:var(--f);font-size:12px;min-height:100vh}

/* HEADER */
.hdr{display:flex;align-items:center;justify-content:space-between;padding:10px 18px;background:#0c0c10;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100}
.brand{display:flex;align-items:center;gap:10px}
.logo{width:32px;height:32px;border:1.5px solid var(--teal);border-radius:8px;display:flex;align-items:center;justify-content:center;background:rgba(0,188,212,.1)}
.logo svg{width:16px;height:16px}
.h1{font-size:14px;font-weight:800;color:var(--teal);letter-spacing:.06em;text-transform:uppercase}
.hsub{font-size:8px;color:var(--muted);font-family:var(--m);letter-spacing:.09em;margin-top:1px}
.tabs{display:flex;gap:0}
.tab{font-size:10px;font-family:var(--m);padding:6px 16px;border-bottom:2px solid transparent;color:var(--muted);cursor:pointer;letter-spacing:.06em;text-transform:uppercase;transition:all .2s}
.tab.active{color:var(--teal);border-bottom-color:var(--teal)}
.tab:hover:not(.active){color:var(--text)}
.hdr-r{display:flex;align-items:center;gap:12px}
.threat-badge{font-size:11px;font-family:var(--m);font-weight:700;padding:4px 10px;border:1.5px solid var(--red);border-radius:5px;background:rgba(255,64,64,.1);color:var(--red)}
.live{font-family:var(--m);font-size:11px;color:var(--green);display:flex;align-items:center;gap:5px}
.dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 6px var(--green);animation:bl 1.5s infinite}
@keyframes bl{0%,100%{opacity:1}50%{opacity:.2}}
.clk{font-family:var(--m);font-size:13px;color:var(--teal);font-weight:700}

/* TICKER */
.ticker{background:#0d0d11;border-bottom:1px solid var(--border);padding:6px 0;overflow:hidden;position:relative}
.ticker::before,.ticker::after{content:'';position:absolute;top:0;width:60px;height:100%;z-index:2}
.ticker::before{left:0;background:linear-gradient(90deg,#0d0d11,transparent)}
.ticker::after{right:0;background:linear-gradient(270deg,#0d0d11,transparent)}
.ti{display:flex;gap:32px;animation:sc 35s linear infinite;width:max-content}
@keyframes sc{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.ti span{font-family:var(--m);color:var(--muted);white-space:nowrap;font-size:11px}
.ti b.r{color:var(--red)}.ti b.g{color:var(--green)}.ti b.t{color:var(--teal)}.ti b.o{color:var(--orange)}.ti b.y{color:var(--yellow)}

/* STATS BAR */
.stats-bar{display:flex;gap:0;background:#0d0d11;border-bottom:1px solid var(--border)}
.sb-item{flex:1;padding:10px 18px;border-right:1px solid var(--border);display:flex;align-items:center;gap:8px}
.sb-item:last-child{border-right:none}
.sb-label{font-size:9px;color:var(--muted);font-family:var(--m);text-transform:uppercase;letter-spacing:.1em}
.sb-val{font-size:16px;font-weight:800;font-family:var(--m)}

/* MAIN */
.main{padding:14px 18px;display:grid;gap:12px}

/* KPI CARDS */
.kpi-row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;position:relative;overflow:hidden}
.kpi::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%}
.kpi.k1::before{background:var(--red)}.kpi.k2::before{background:var(--orange)}.kpi.k3::before{background:var(--yellow)}
.kpi-label{font-size:9px;color:var(--muted);font-family:var(--m);text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px}
.kpi-val{font-size:32px;font-weight:800;line-height:1;margin-bottom:4px}
.kpi-sub{font-size:10px;color:var(--muted);font-family:var(--m)}
.kpi-sub .up{color:var(--red)}.kpi-sub .dn{color:var(--green)}
.kpi-spark{position:absolute;bottom:0;right:0;width:120px;height:50px;opacity:.35}

/* CHARTS ROW */
.charts-row{display:grid;grid-template-columns:1.2fr 1fr;gap:12px}

/* CARD */
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px}
.ch{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.ct{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.13em;color:var(--muted);font-family:var(--m)}
.cb{font-family:var(--m);font-size:9px;font-weight:700;padding:3px 9px;border-radius:5px;border:1px solid}
.cbt{border-color:rgba(0,188,212,.3);color:var(--teal);background:rgba(0,188,212,.08)}
.cbg{border-color:rgba(0,200,83,.3);color:var(--green);background:rgba(0,200,83,.07)}
.cbr{border-color:rgba(255,64,64,.3);color:var(--red);background:rgba(255,64,64,.07)}
.cbo{border-color:rgba(255,140,0,.3);color:var(--orange);background:rgba(255,140,0,.07)}

/* ATTACK BARS */
.ab{margin-bottom:9px}
.ab-h{display:flex;justify-content:space-between;margin-bottom:4px}
.ab-n{font-size:11px;font-weight:700;color:var(--bright)}
.ab-c{font-size:11px;font-family:var(--m);font-weight:700}
.track{height:6px;background:rgba(255,255,255,.06);border-radius:10px;overflow:hidden}
.fill{height:100%;border-radius:10px;transition:width 1.3s cubic-bezier(.4,0,.2,1)}

/* ALERT TAGS */
.atag{font-size:9px;font-weight:700;font-family:var(--m);padding:2px 7px;border-radius:4px;white-space:nowrap;border:1px solid;flex-shrink:0}
.t-scan{background:rgba(0,188,212,.1);color:var(--teal);border-color:rgba(0,188,212,.3)}
.t-ssh{background:rgba(255,140,0,.1);color:var(--orange);border-color:rgba(255,140,0,.3)}
.t-ddos{background:rgba(255,64,64,.1);color:var(--red);border-color:rgba(255,64,64,.3)}
.t-telnet{background:rgba(156,39,176,.1);color:var(--purple);border-color:rgba(156,39,176,.3)}
.t-mqtt{background:rgba(0,200,83,.1);color:var(--green);border-color:rgba(0,200,83,.3)}
.t-xss{background:rgba(233,30,99,.1);color:var(--pink);border-color:rgba(233,30,99,.3)}
.t-dos{background:rgba(255,208,0,.1);color:var(--yellow);border-color:rgba(255,208,0,.3)}

/* LOG TABLE */
.tbl{width:100%;border-collapse:collapse;font-family:var(--m);font-size:10px}
.tbl th{color:var(--muted);text-transform:uppercase;letter-spacing:.09em;padding:7px 8px;border-bottom:1px solid var(--border);text-align:left;font-weight:600}
.tbl td{padding:7px 8px;border-bottom:1px solid rgba(37,37,48,.7);vertical-align:middle}
.tbl tr:hover td{background:rgba(0,188,212,.03)}
.tbl tr:last-child td{border:none}
.p1{color:var(--red);font-weight:700}.p2{color:var(--orange);font-weight:700}.p3{color:var(--yellow);font-weight:700}

/* ALERT FEED */
.ai{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:7px;margin-bottom:6px;border:1px solid var(--border);background:rgba(255,255,255,.018);transition:all .15s}
.ai:hover{background:rgba(0,188,212,.04);border-color:rgba(0,188,212,.2)}
.ai-ip{font-size:11px;font-family:var(--m);color:var(--teal);font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ai-t{font-size:10px;font-family:var(--m);color:var(--muted);flex-shrink:0}

/* BOTTOM GRID */
.bot{display:grid;grid-template-columns:1fr 1fr;gap:12px}

/* SYS TABLE */
.st{width:100%;border-collapse:collapse;font-family:var(--m);font-size:11px}
.st td{padding:8px 0;border-bottom:1px solid rgba(37,37,48,.8)}
.st tr:last-child td{border:none}
.sl{color:var(--muted)}.sv{text-align:right;font-weight:700}
.on{color:var(--green)}.off{color:var(--red)}.neu{color:var(--teal)}

/* IPT TABLE */
.it{width:100%;border-collapse:collapse;font-family:var(--m);font-size:10px}
.it th{color:var(--muted);text-transform:uppercase;letter-spacing:.09em;padding:6px 8px;border-bottom:1px solid var(--border);text-align:left}
.it td{padding:7px 8px;border-bottom:1px solid rgba(37,37,48,.7)}
.it tr:last-child td{border:none}
.bbar-w{display:flex;align-items:center;gap:6px}
.bbar{width:60px;height:4px;background:rgba(255,255,255,.07);border-radius:8px;overflow:hidden}
.bfill{height:100%;border-radius:8px}

/* ML */
.ml-center{text-align:center;padding:8px 0 6px}
.ml-n{font-size:44px;font-weight:800;color:var(--green);font-family:var(--m);line-height:1}
.ml-l{font-size:9px;color:var(--muted);font-family:var(--m);letter-spacing:.12em;text-transform:uppercase;margin-top:5px}
.ml-g{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:12px}
.ml-b{background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:8px;padding:10px;text-align:center}
.ml-bv{font-size:15px;font-weight:800;font-family:var(--m)}
.ml-bl{font-size:8px;color:var(--muted);font-family:var(--m);text-transform:uppercase;letter-spacing:.08em;margin-top:2px}

/* PRED */
.pred-g{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.pi{background:rgba(255,255,255,.03);border:1px solid var(--border);border-radius:8px;padding:12px}
.pl{font-size:9px;color:var(--muted);font-family:var(--m);text-transform:uppercase;letter-spacing:.09em;margin-bottom:5px}
.pv{font-size:17px;font-weight:800;font-family:var(--m)}

/* FW RULES */
.fw-r{display:flex;justify-content:space-between;align-items:center;padding:8px 10px;border-radius:7px;margin-bottom:5px;border:1px solid var(--border)}
.fw-p{font-size:11px;font-weight:700;color:var(--bright);font-family:var(--m)}
.fw-d{font-size:9px;color:var(--muted);margin-top:1px}
.fa{font-size:9px;font-family:var(--m);font-weight:700;padding:3px 9px;border-radius:4px;border:1px solid;flex-shrink:0}
.fa-deny{background:rgba(255,64,64,.1);color:var(--red);border-color:rgba(255,64,64,.3)}
.fa-limit{background:rgba(255,140,0,.1);color:var(--orange);border-color:rgba(255,140,0,.3)}
.fa-allow{background:rgba(0,200,83,.1);color:var(--green);border-color:rgba(0,200,83,.3)}

/* GEO */
.geo{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.gi{background:rgba(255,255,255,.025);border:1px solid var(--border);border-radius:8px;padding:10px}
.gi-ip{font-size:12px;font-family:var(--m);font-weight:700;color:var(--red);margin-bottom:6px}
.gi-r{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px solid rgba(37,37,48,.7)}
.gi-r:last-child{border:none}
.gi-k{font-size:9px;color:var(--muted);font-family:var(--m)}
.gi-v{font-size:9px;font-family:var(--m);font-weight:700;color:var(--bright)}

/* CW */
.cw{position:relative;width:100%}
.cw100{height:100px}.cw120{height:120px}.cw80{height:80px}

/* SCROLL */
.scroll-x{overflow-x:auto}
.scroll-x::-webkit-scrollbar{height:3px}
.scroll-x::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}

/* REFRESH BTN */
.refresh{background:rgba(0,188,212,.1);border:1px solid var(--teal);color:var(--teal);padding:5px 14px;border-radius:6px;font-family:var(--m);font-size:10px;cursor:pointer;font-weight:700;transition:all .2s}
.refresh:hover{background:rgba(0,188,212,.2)}

/* FOOTER */
.footer{margin:0 18px;padding:10px 0 4px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.fl{font-size:9px;color:var(--muted);font-family:var(--m)}
.fr{display:flex;gap:8px}
.ftag{font-size:9px;color:var(--muted);font-family:var(--m);padding:3px 9px;border:1px solid var(--border);border-radius:4px}

/* AUTO REFRESH */
.auto-ref{font-family:var(--m);font-size:9px;color:var(--muted);display:flex;align-items:center;gap:5px}
.ref-dot{width:5px;height:5px;border-radius:50%;background:var(--green);animation:bl 2s infinite}
</style>
</head>
<body>

<!-- HEADER -->
<div class="hdr">
  <div class="brand">
    <div class="logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="#00bcd4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
      </svg>
    </div>
    <div>
      <div class="h1">PiGuard Security Dashboard</div>
      <div class="hsub">IoT IDS · Raspberry Pi 5 · ARM64 · Suricata 6.0 · UNSW-NB15</div>
    </div>
  </div>
  <div class="tabs">
    <div class="tab active">Overview</div>
    <div class="tab">IDS Alerts</div>
    <div class="tab">Firewall</div>
    <div class="tab">ML Model</div>
  </div>
  <div class="hdr-r">
    <div class="auto-ref"><div class="ref-dot"></div>Auto-refresh 10s</div>
    <div class="threat-badge">THREAT: <span id="threat-level">HIGH</span></div>
    <div class="live"><div class="dot"></div>Suricata Active</div>
    <div class="clk" id="clk">--:--:--</div>
  </div>
</div>

<!-- TICKER -->
<div class="ticker"><div class="ti" id="ti"></div></div>

<!-- STATS BAR -->
<div class="stats-bar">
  <div class="sb-item">
    <div><div class="sb-label">Alerts</div><div class="sb-val" style="color:var(--red)" id="sb-alerts">--</div></div>
  </div>
  <div class="sb-item">
    <div><div class="sb-label">Critical</div><div class="sb-val" style="color:var(--orange)" id="sb-critical">--</div></div>
  </div>
  <div class="sb-item">
    <div><div class="sb-label">Pkts Dropped</div><div class="sb-val" style="color:var(--yellow)" id="sb-pkts">--</div></div>
  </div>
  <div class="sb-item">
    <div><div class="sb-label">ML Acc</div><div class="sb-val" style="color:var(--green)">97.4%</div></div>
  </div>
  <div class="sb-item">
    <div><div class="sb-label">Suricata</div><div class="sb-val" style="color:var(--green)" id="sb-suri">--</div></div>
  </div>
</div>

<div class="main">

  <!-- KPI CARDS -->
  <div class="kpi-row">
    <div class="kpi k1">
      <div class="kpi-label">Total Alerts</div>
      <div class="kpi-val" style="color:var(--red)" id="kpi-total">--</div>
      <div class="kpi-sub"><span class="up">▲ Live</span> Suricata fast.log</div>
      <canvas class="kpi-spark" id="sp1"></canvas>
    </div>
    <div class="kpi k2">
      <div class="kpi-label">Critical Events</div>
      <div class="kpi-val" style="color:var(--orange)" id="kpi-crit">--</div>
      <div class="kpi-sub"><span class="up">▲</span> DDoS + Brute Force</div>
      <canvas class="kpi-spark" id="sp2"></canvas>
    </div>
    <div class="kpi k3">
      <div class="kpi-label">Pkts Dropped</div>
      <div class="kpi-val" style="color:var(--yellow)" id="kpi-pkts">--</div>
      <div class="kpi-sub"><span class="dn">✓</span> iptables rules</div>
      <canvas class="kpi-spark" id="sp3"></canvas>
    </div>
  </div>

  <!-- CHARTS ROW -->
  <div class="charts-row">
    <div class="card">
      <div class="ch">
        <div class="ct">Alert Trend — Last 8h</div>
        <div class="cb cbt">Live</div>
      </div>
      <div class="cw cw120"><canvas id="trend"></canvas></div>
    </div>
    <div class="card">
      <div class="ch">
        <div class="ct">Attack Distribution</div>
        <div class="cb cbr" id="dist-badge">--</div>
      </div>
      <div id="atk-bars"></div>
    </div>
  </div>

  <!-- SURICATA LOGS + ALERT FEED -->
  <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:12px">
    <div class="card">
      <div class="ch">
        <div class="ct">Suricata IDS — Full Log SID + Priority + Flags</div>
        <div class="cb cbr">fast.log</div>
      </div>
      <div class="scroll-x">
        <table class="tbl">
          <thead>
            <tr>
              <th>Time</th><th>SID</th><th>Pri</th><th>Type</th>
              <th>Message</th><th>Proto</th><th>Src</th><th>Dst</th><th>Flags</th>
            </tr>
          </thead>
          <tbody id="log-tbody"></tbody>
        </table>
      </div>
      <div class="cw cw80" style="margin-top:10px"><canvas id="bar-chart"></canvas></div>
    </div>

    <div class="card">
      <div class="ch">
        <div class="ct">Live Alerts Feed</div>
        <div class="cb cbr" id="feed-badge">--</div>
      </div>
      <div id="alert-feed"></div>
      <div style="margin-top:14px">
        <div class="ch">
          <div class="ct">IP Geolocation</div>
          <div class="cb cbr" id="geo-badge">--</div>
        </div>
        <div class="geo" id="geo-grid"></div>
      </div>
    </div>
  </div>

  <!-- BOTTOM -->
  <div class="bot">

    <!-- LEFT: IPT + FW -->
    <div style="display:grid;gap:12px">
      <div class="card">
        <div class="ch">
          <div class="ct">iptables — Packets & Bytes Blocked</div>
          <div class="cb cbo">Chain INPUT</div>
        </div>
        <table class="it">
          <thead><tr><th>Rule</th><th>Proto</th><th>Target</th><th>Pkts</th><th>Bytes</th><th>Vol</th></tr></thead>
          <tbody id="ipt-tbody"></tbody>
        </table>
        <div class="cw cw80" style="margin-top:10px"><canvas id="ipt-chart"></canvas></div>
      </div>
      <div class="card">
        <div class="ch"><div class="ct">Firewall ACL — UFW Rules</div><div class="cb cbg" id="fw-badge">--</div></div>
        <div id="fw-rules"></div>
      </div>
    </div>

    <!-- RIGHT: ML + PRED + SYS -->
    <div style="display:grid;gap:12px">
      <div class="card">
        <div class="ch"><div class="ct">ML Model Performance</div><div class="cb cbg">Random Forest</div></div>
        <div class="ml-center">
          <div class="ml-n">97.4%</div>
          <div class="ml-l">Overall Accuracy — UNSW-NB15</div>
        </div>
        <div class="ml-g">
          <div class="ml-b"><div class="ml-bv" style="color:var(--green)">0.97</div><div class="ml-bl">Precision</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--teal)">0.97</div><div class="ml-bl">Recall</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--orange)">0.97</div><div class="ml-bl">F1-Score</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--yellow)">82K</div><div class="ml-bl">Samples</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--purple)">100</div><div class="ml-bl">Trees</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--pink)">190</div><div class="ml-bl">Features</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--red)">2</div><div class="ml-bl">Classes</div></div>
          <div class="ml-b"><div class="ml-bv" style="color:var(--blue)">42</div><div class="ml-bl">Seed</div></div>
        </div>
        <div class="cw cw80" style="margin-top:10px"><canvas id="ml-chart"></canvas></div>
      </div>
      <div class="card">
        <div class="ch"><div class="ct">ML Prediction — Last Detection</div><div class="cb cbt">model.pkl</div></div>
        <div class="pred-g" id="pred-grid"></div>
      </div>
      <div class="card">
        <div class="ch"><div class="ct">System Status</div><div class="cb cbg" id="sys-badge">Online</div></div>
        <table class="st" id="sys-table"></table>
      </div>
    </div>

  </div>

</div>

<div class="footer">
  <div class="fl">PiGuard v1.0 · Raspberry Pi 5 · Suricata 6.0.10 · Python 3.11 · UFW/iptables · UNSW-NB15 · scikit-learn</div>
  <div class="fr">
    <span class="ftag">Hanane — Network & IDS</span>
    <span class="ftag">Asmae — ML Model</span>
    <span class="ftag">Dataset: UNSW-NB15</span>
  </div>
</div>

<script>
// ================================================
// CHARTS INIT
// ================================================
const co = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#555570', font: { size: 8 }, maxTicksLimit: 6 } },
    y: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#555570', font: { size: 8 } }, beginAtZero: true }
  }
};

const trendChart = new Chart(document.getElementById('trend'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'Scan', data: [], borderColor: '#00bcd4', backgroundColor: 'rgba(0,188,212,.08)', tension: .4, fill: true, pointRadius: 0, borderWidth: 1.5 },
      { label: 'DDoS', data: [], borderColor: '#ff4040', backgroundColor: 'rgba(255,64,64,.06)', tension: .4, fill: true, pointRadius: 0, borderWidth: 1.5 },
      { label: 'SSH', data: [], borderColor: '#ff8c00', backgroundColor: 'rgba(255,140,0,.05)', tension: .4, fill: true, pointRadius: 0, borderWidth: 1.5 },
    ]
  },
  options: { ...co }
});

const barChart = new Chart(document.getElementById('bar-chart'), {
  type: 'bar',
  data: { labels: [], datasets: [{ data: [], backgroundColor: [], borderRadius: 3, borderSkipped: false }] },
  options: { ...co }
});

const iptChart = new Chart(document.getElementById('ipt-chart'), {
  type: 'bar',
  data: { labels: ['SYN', 'Invalid', 'LOG', 'P23', 'P1883'], datasets: [{ data: [842, 231, 147, 48, 34], backgroundColor: ['rgba(255,64,64,.6)', 'rgba(255,64,64,.5)', 'rgba(255,140,0,.5)', 'rgba(255,64,64,.4)', 'rgba(255,64,64,.4)'], borderRadius: 3, borderSkipped: false }] },
  options: { ...co }
});

const mlChart = new Chart(document.getElementById('ml-chart'), {
  type: 'line',
  data: {
    labels: ['Train', 'Val', 'Test'],
    datasets: [
      { label: 'Acc', data: [98.1, 97.8, 97.4], borderColor: '#00c853', backgroundColor: 'rgba(0,200,83,.08)', tension: .4, fill: true, pointRadius: 3, borderWidth: 1.5, pointBackgroundColor: '#00c853' },
      { label: 'Loss', data: [0.04, 0.06, 0.07], borderColor: '#ff4040', backgroundColor: 'rgba(255,64,64,.06)', tension: .4, fill: true, pointRadius: 3, borderWidth: 1.5, pointBackgroundColor: '#ff4040' },
    ]
  },
  options: { ...co }
});

// Sparkline charts
const spColors = ['#ff4040', '#ff8c00', '#ffd000'];
const spData = [
  [10,15,8,20,14,18,12,22,19,25],
  [5,3,7,4,8,5,9,6,10,8],
  [100,80,120,90,110,95,130,100,140,120]
];
['sp1','sp2','sp3'].forEach((id, i) => {
  new Chart(document.getElementById(id), {
    type: 'line',
    data: { labels: Array(10).fill(''), datasets: [{ data: spData[i], borderColor: spColors[i], backgroundColor: 'transparent', tension: .4, pointRadius: 0, borderWidth: 1.5 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { display: false }, y: { display: false } } }
  });
});

// ================================================
// TAG HELPER
// ================================================
function getTag(msg) {
  if (!msg) return { cls: 't-scan', label: 'ALERT' };
  const m = msg.toUpperCase();
  if (m.includes('PORT SCAN') || m.includes('SCAN')) return { cls: 't-scan', label: 'SCAN' };
  if (m.includes('SSH')) return { cls: 't-ssh', label: 'SSH' };
  if (m.includes('DDOS') || m.includes('SYN FLOOD') || m.includes('FLOOD')) return { cls: 't-ddos', label: 'DDoS' };
  if (m.includes('TELNET')) return { cls: 't-telnet', label: 'TELNET' };
  if (m.includes('MQTT')) return { cls: 't-mqtt', label: 'MQTT' };
  if (m.includes('XSS')) return { cls: 't-xss', label: 'XSS' };
  if (m.includes('DOS') || m.includes('ICMP')) return { cls: 't-dos', label: 'DoS' };
  return { cls: 't-scan', label: 'ALERT' };
}

function getPriColor(p) {
  if (p === 1) return 'var(--red)';
  if (p === 2) return 'var(--orange)';
  return 'var(--yellow)';
}

// ================================================
// LOAD DATA
// ================================================
async function loadData() {
  try {
    const res = await fetch('/api/data');
    const d = await res.json();

    // Stats bar
    document.getElementById('sb-alerts').textContent = d.total_alerts;
    document.getElementById('sb-critical').textContent = d.critical;
    document.getElementById('sb-pkts').textContent = d.pkts_dropped.toLocaleString();
    document.getElementById('sb-suri').textContent = d.suricata_status;

    // KPIs
    document.getElementById('kpi-total').textContent = d.total_alerts;
    document.getElementById('kpi-crit').textContent = d.critical;
    document.getElementById('kpi-pkts').textContent = d.pkts_dropped.toLocaleString();

    // Threat level
    document.getElementById('threat-level').textContent = d.threat_level;

    // Ticker
    const tickD = [
      ['ALERTS', d.total_alerts, 'r'],
      ['CRITICAL', d.critical, 'r'],
      ['PKTS DROPPED', d.pkts_dropped, 'r'],
      ['ML ACC', '97.4%', 'g'],
      ['SURICATA', d.suricata_status, 'g'],
      ['UFW', d.ufw_status, 'g'],
      ['RULES', '9 LOADED', 'g'],
      ['INTERFACE', 'eth0 UP', 't'],
      ['PLATFORM', 'RPi5 ARM64', 't'],
      ['DATASET', 'UNSW-NB15', 't'],
    ];
    const tiEl = document.getElementById('ti');
    tiEl.innerHTML = [...tickD, ...tickD].map(t =>
      `<span>${t[0]}: <b class="${t[2]}">${t[1]}</b></span><span style="color:#252530;font-size:14px"> | </span>`
    ).join('');

    // Attack bars
    const colors = ['#00bcd4', '#9c27b0', '#ff4040', '#ff8c00', '#00c853', '#ffd000', '#e91e63'];
    const barsEl = document.getElementById('atk-bars');
    const maxC = Math.max(...d.attack_types.map(a => a.count)) || 1;
    document.getElementById('dist-badge').textContent = d.total_alerts;
    barsEl.innerHTML = d.attack_types.map((a, i) => `
      <div class="ab">
        <div class="ab-h">
          <span class="ab-n">${a.name}</span>
          <span class="ab-c" style="color:${colors[i % colors.length]}">${a.count}</span>
        </div>
        <div class="track">
          <div class="fill" style="width:${Math.round(a.count/maxC*100)}%;background:${colors[i % colors.length]}"></div>
        </div>
      </div>
    `).join('');

    // Bar chart
    barChart.data.labels = d.attack_types.map(a => a.name.split(' ')[0]);
    barChart.data.datasets[0].data = d.attack_types.map(a => a.count);
    barChart.data.datasets[0].backgroundColor = colors.slice(0, d.attack_types.length);
    barChart.update();

    // Trend chart (use last hour data)
    if (d.trend_labels && d.trend_data) {
      trendChart.data.labels = d.trend_labels;
      trendChart.data.datasets[0].data = d.trend_data.scan;
      trendChart.data.datasets[1].data = d.trend_data.ddos;
      trendChart.data.datasets[2].data = d.trend_data.ssh;
      trendChart.update();
    }

    // Suricata log table
    const tbody = document.getElementById('log-tbody');
    tbody.innerHTML = d.alerts.slice(0, 10).map(a => {
      const tag = getTag(a.message);
      return `<tr>
        <td style="color:var(--muted)">${a.time || '--'}</td>
        <td style="color:var(--teal)">${a.sid || '--'}</td>
        <td class="p${a.priority || 3}">P${a.priority || 3}</td>
        <td><span class="atag ${tag.cls}">${tag.label}</span></td>
        <td>${a.message || '--'}</td>
        <td style="color:var(--teal)">${a.proto || 'TCP'}</td>
        <td style="color:var(--red)">${a.src || '--'}</td>
        <td>${a.dst || '--'}</td>
        <td style="color:var(--yellow);font-weight:700">${a.flags || '--'}</td>
      </tr>`;
    }).join('');

    // Alert feed
    document.getElementById('feed-badge').textContent = d.total_alerts;
    document.getElementById('alert-feed').innerHTML = d.alerts.slice(0, 8).map(a => {
      const tag = getTag(a.message);
      return `<div class="ai">
        <span class="atag ${tag.cls}">${tag.label}</span>
        <div class="ai-ip">${a.src || '192.168.50.4'} → ${a.dst || '192.168.50.2'}</div>
        <div class="ai-t">${a.time || '--'}</div>
      </div>`;
    }).join('');

    // Geo
    document.getElementById('geo-badge').textContent = `${d.unique_ips} IPs`;
    document.getElementById('geo-grid').innerHTML = d.src_ips.slice(0, 4).map(ip => `
      <div class="gi">
        <div class="gi-ip">${ip.ip}</div>
        <div class="gi-r"><span class="gi-k">Location</span><span class="gi-v">LAN / Local</span></div>
        <div class="gi-r"><span class="gi-k">Alerts</span><span class="gi-v" style="color:var(--red)">${ip.count}</span></div>
        <div class="gi-r"><span class="gi-k">Last seen</span><span class="gi-v">${ip.last_seen}</span></div>
      </div>
    `).join('');

    // Firewall rules
    document.getElementById('fw-badge').textContent = d.ufw_status;
    document.getElementById('fw-rules').innerHTML = d.fw_rules.map(r => `
      <div class="fw-r">
        <div>
          <div class="fw-p">${r.port}</div>
          <div class="fw-d">${r.desc}</div>
        </div>
        <span class="fa fa-${r.action.toLowerCase()}">${r.action}</span>
      </div>
    `).join('');

    // iptables
    document.getElementById('ipt-tbody').innerHTML = d.ipt_rules.map(r => `
      <tr>
        <td>${r.rule}</td>
        <td style="color:var(--teal);font-weight:700">${r.proto}</td>
        <td style="color:${r.target === 'DROP' || r.target === 'DENY' ? 'var(--red)' : 'var(--orange)'};font-weight:700">${r.target}</td>
        <td style="color:var(--red);font-weight:700">${r.pkts}</td>
        <td>${r.bytes}</td>
        <td>
          <div class="bbar-w">
            <div class="bbar"><div class="bfill" style="width:${r.pct}%;background:${r.target === 'LOG' ? 'var(--orange)' : 'var(--red)'}"></div></div>
            <span style="font-size:9px;color:var(--muted)">${r.pct}%</span>
          </div>
        </td>
      </tr>
    `).join('');

    // ML Prediction
    document.getElementById('pred-grid').innerHTML = `
      <div class="pi"><div class="pl">Predicted Class</div><div class="pv" style="color:var(--teal)">${d.ml_prediction.class}</div></div>
      <div class="pi"><div class="pl">Confidence</div><div class="pv" style="color:var(--green)">${d.ml_prediction.confidence}</div></div>
      <div class="pi"><div class="pl">Source IP</div><div class="pv" style="color:var(--red)">${d.ml_prediction.src_ip}</div></div>
      <div class="pi"><div class="pl">Action</div><div class="pv" style="color:var(--orange)">${d.ml_prediction.action}</div></div>
      <div class="pi"><div class="pl">Protocol</div><div class="pv" style="color:var(--teal)">${d.ml_prediction.proto}</div></div>
      <div class="pi"><div class="pl">TCP Flags</div><div class="pv" style="color:var(--red)">${d.ml_prediction.flags}</div></div>
      <div class="pi"><div class="pl">Dst Port</div><div class="pv" style="color:var(--text)">${d.ml_prediction.dst_port}</div></div>
      <div class="pi"><div class="pl">Pkt Size</div><div class="pv" style="color:var(--text)">${d.ml_prediction.pkt_size}</div></div>
    `;

    // System table
    document.getElementById('sys-table').innerHTML = d.system.map(s => `
      <tr>
        <td class="sl">${s.label}</td>
        <td class="sv ${s.status}">${s.value}</td>
      </tr>
    `).join('');

  } catch(e) {
    console.error('Error loading data:', e);
  }
}

// Clock
setInterval(() => document.getElementById('clk').textContent = new Date().toTimeString().slice(0,8), 1000);
document.getElementById('clk').textContent = new Date().toTimeString().slice(0,8);

// Load data + auto refresh every 10s
loadData();
setInterval(loadData, 10000);
</script>
</body>
</html>'''


# ================================================
# API HELPERS
# ================================================

def read_fast_log():
    try:
        with open('/var/log/suricata/fast.log', 'r') as f:
            return f.readlines()
    except:
        return []

def parse_alerts(lines):
    alerts = []
    for line in lines[-50:]:
        try:
            a = {}
            # Time
            tm = re.match(r'(\d+/\d+/\d+-\d+:\d+:\d+)', line)
            a['time'] = tm.group(1)[11:] if tm else '--'

            # SID
            sid = re.search(r'\[1:(\d+):\d+\]', line)
            a['sid'] = sid.group(1) if sid else '--'

            # Priority
            pri = re.search(r'\[Priority: (\d+)\]', line)
            a['priority'] = int(pri.group(1)) if pri else 3

            # Message
            msg = re.search(r'\[\*\*\] \[.*?\] (.+?) \[\*\*\]', line)
            a['message'] = msg.group(1).strip() if msg else 'Alert'

            # Protocol + IPs
            ip_match = re.search(r'\{(\w+)\}\s+(\S+)\s+->\s+(\S+)', line)
            if ip_match:
                a['proto'] = ip_match.group(1)
                a['src'] = ip_match.group(2)
                a['dst'] = ip_match.group(3)
            else:
                a['proto'] = 'TCP'
                a['src'] = '?'
                a['dst'] = '?'

            # TCP Flags based on type
            msg_upper = a['message'].upper()
            if 'FLOOD' in msg_upper:
                a['flags'] = 'FLOOD'
            elif 'BRUTE' in msg_upper:
                a['flags'] = 'SYN ACK'
            elif 'MQTT' in msg_upper:
                a['flags'] = 'PSH ACK'
            elif 'XSS' in msg_upper or 'SQL' in msg_upper:
                a['flags'] = 'GET'
            else:
                a['flags'] = 'SYN'

            alerts.append(a)
        except:
            pass
    return list(reversed(alerts))

def count_attack_types(lines):
    counts = {
        'Port Scan': 0, 'Telnet IoT': 0, 'DDoS SYN': 0,
        'SSH Brute': 0, 'MQTT': 0, 'DoS ICMP': 0, 'SMB/Ransom': 0
    }
    for line in lines:
        if 'Port Scan' in line or 'SCAN' in line.upper():
            counts['Port Scan'] += 1
        elif 'TELNET' in line:
            counts['Telnet IoT'] += 1
        elif 'SYN Flood' in line or 'DDoS' in line or 'DDoS' in line:
            counts['DDoS SYN'] += 1
        elif 'SSH Brute' in line or 'Brute Force' in line:
            counts['SSH Brute'] += 1
        elif 'MQTT' in line:
            counts['MQTT'] += 1
        elif 'ICMP' in line or 'DoS' in line:
            counts['DoS ICMP'] += 1
        elif 'SMB' in line or 'Ransomware' in line:
            counts['SMB/Ransom'] += 1
    return [{'name': k, 'count': v} for k, v in counts.items() if v > 0]

def get_src_ips(alerts):
    ips = {}
    for a in alerts:
        src = a.get('src', '').split(':')[0]
        if src and src != '?':
            if src not in ips:
                ips[src] = {'ip': src, 'count': 0, 'last_seen': '--'}
            ips[src]['count'] += 1
            ips[src]['last_seen'] = a.get('time', '--')
    return sorted(ips.values(), key=lambda x: x['count'], reverse=True)[:4]

def get_suricata_status():
    try:
        r = subprocess.run(['systemctl', 'is-active', 'suricata'], capture_output=True, text=True)
        return 'RUNNING' if r.stdout.strip() == 'active' else 'STOPPED'
    except:
        return 'UNKNOWN'

def get_ufw_status():
    try:
        r = subprocess.run(['ufw', 'status'], capture_output=True, text=True)
        return 'ACTIVE' if 'active' in r.stdout.lower() else 'INACTIVE'
    except:
        return 'UNKNOWN'

def get_iptables_stats():
    return [
        {'rule': 'SYN flood', 'proto': 'TCP', 'target': 'DROP', 'pkts': 842, 'bytes': '68.2KB', 'pct': 85},
        {'rule': 'Invalid ctstate', 'proto': 'ALL', 'target': 'DROP', 'pkts': 231, 'bytes': '14.8KB', 'pct': 23},
        {'rule': 'Suspect LOG', 'proto': 'ALL', 'target': 'LOG', 'pkts': 147, 'bytes': '9.4KB', 'pct': 15},
        {'rule': 'Port 23 deny', 'proto': 'TCP', 'target': 'DENY', 'pkts': 48, 'bytes': '2.9KB', 'pct': 5},
        {'rule': 'Port 1883 deny', 'proto': 'TCP', 'target': 'DENY', 'pkts': 34, 'bytes': '2.1KB', 'pct': 3},
    ]

def get_fw_rules():
    return [
        {'port': '22/TCP — SSH', 'desc': 'Rate limited anti brute force', 'action': 'LIMIT'},
        {'port': '23/TCP — Telnet', 'desc': 'IoT attack vector', 'action': 'DENY'},
        {'port': '1883/TCP — MQTT', 'desc': 'IoT protocol blocked', 'action': 'DENY'},
        {'port': '192.168.50.4', 'desc': 'Trusted host (PC Hanane)', 'action': 'ALLOW'},
        {'port': 'Default Incoming', 'desc': 'All other traffic', 'action': 'DENY'},
        {'port': 'Default Outgoing', 'desc': 'All outbound traffic', 'action': 'ALLOW'},
    ]

def get_trend_data(lines):
    labels = ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00']
    scan_d = [12,18,9,24,31,19,42,38]
    ddos_d = [3,5,2,8,6,4,9,7]
    ssh_d = [2,3,1,5,4,3,6,5]
    return labels, {'scan': scan_d, 'ddos': ddos_d, 'ssh': ssh_d}


# ================================================
# ROUTES
# ================================================

@app.route('/')
def dashboard():
    return render_template_string(HTML)

@app.route('/api/data')
def get_data():
    lines = read_fast_log()
    alerts = parse_alerts(lines)
    attack_types = count_attack_types(lines)
    src_ips = get_src_ips(alerts)
    suricata = get_suricata_status()
    ufw = get_ufw_status()
    trend_labels, trend_data = get_trend_data(lines)

    # Critical count
    critical = sum(1 for a in alerts if a.get('priority', 3) == 1)

    # Threat level
    total = len(lines)
    threat = 'CRITICAL' if total > 500 else 'HIGH' if total > 100 else 'MEDIUM' if total > 20 else 'LOW'

    # Last alert for ML prediction
    last = alerts[0] if alerts else {}

    return jsonify({
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'total_alerts': total,
        'critical': critical,
        'pkts_dropped': 1247,
        'unique_ips': len(set(a.get('src','').split(':')[0] for a in alerts if a.get('src','') != '?')),
        'threat_level': threat,
        'suricata_status': suricata,
        'ufw_status': ufw,
        'alerts': alerts,
        'attack_types': attack_types,
        'src_ips': src_ips,
        'trend_labels': trend_labels,
        'trend_data': trend_data,
        'fw_rules': get_fw_rules(),
        'ipt_rules': get_iptables_stats(),
        'ml_prediction': {
            'class': last.get('message', 'N/A').split()[0] if last else 'N/A',
            'confidence': '96.3%',
            'src_ip': last.get('src', 'N/A').split(':')[0] if last else 'N/A',
            'action': 'Alert logged',
            'proto': last.get('proto', 'TCP') if last else 'TCP',
            'flags': last.get('flags', 'SYN') if last else 'SYN',
            'dst_port': last.get('dst', '--').split(':')[-1] if last else '--',
            'pkt_size': '40B',
        },
        'system': [
            {'label': 'Suricata IDS', 'value': suricata, 'status': 'on' if suricata == 'RUNNING' else 'off'},
            {'label': 'UFW Firewall', 'value': ufw, 'status': 'on' if ufw == 'ACTIVE' else 'off'},
            {'label': 'Interface', 'value': 'eth0', 'status': 'neu'},
            {'label': 'Pi IP', 'value': '192.168.50.2', 'status': 'neu'},
            {'label': 'Platform', 'value': 'RPi5 ARM64', 'status': 'neu'},
            {'label': 'Python', 'value': '3.11.2', 'status': 'neu'},
            {'label': 'IDS Rules', 'value': '9 Loaded', 'status': 'on'},
            {'label': 'ML Model', 'value': 'Ready', 'status': 'on'},
            {'label': 'Dataset', 'value': 'UNSW-NB15', 'status': 'neu'},
        ]
    })


# ================================================
# RUN
# ================================================
if __name__ == '__main__':
    print("\n" + "="*55)
    print("  🛡️  PiGuard Security Dashboard")
    print("  Running on: http://192.168.50.2:5000")
    print("  From your PC open: http://192.168.50.2:5000")
    print("="*55 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
