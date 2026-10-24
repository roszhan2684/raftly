/* Raftly site: theme, copy buttons, tabs, terminal replay, reveal-on-scroll. No tracking, no network calls. */
(function () {
  "use strict";
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // theme toggle (per-viewer convenience only)
  var themeBtn = document.getElementById("theme");
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    if (themeBtn) {
      themeBtn.textContent = t === "dark" ? "☀" : "☾";
      themeBtn.setAttribute("aria-label", t === "dark" ? "Switch to light theme" : "Switch to dark theme");
    }
  }
  var saved = null;
  try { saved = localStorage.getItem("raftly-theme"); } catch (e) { /* storage unavailable */ }
  var sysDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
  applyTheme(saved || (sysDark ? "dark" : "light"));
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem("raftly-theme", next); } catch (e) { /* ignore */ }
  });

  // copy buttons
  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.getAttribute("data-copy");
      var done = function () { var o = btn.textContent; btn.textContent = "Copied"; setTimeout(function () { btn.textContent = o; }, 1400); };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(done, function () { fallback(text); done(); });
      } else { fallback(text); done(); }
    });
  });
  function fallback(text) {
    var ta = document.createElement("textarea");
    ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "absolute"; ta.style.left = "-9999px";
    document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e) { /* ignore */ }
    document.body.removeChild(ta);
  }

  // tabs (WAI-ARIA tabs pattern with arrow keys)
  document.querySelectorAll("[role=tablist]").forEach(function (list) {
    var tabs = Array.prototype.slice.call(list.querySelectorAll("[role=tab]"));
    function select(tab) {
      tabs.forEach(function (t) {
        var on = t === tab;
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
        var panel = document.getElementById(t.getAttribute("aria-controls"));
        if (panel) panel.hidden = !on;
      });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(t); });
      t.addEventListener("keydown", function (e) {
        var j = null;
        if (e.key === "ArrowRight") j = (i + 1) % tabs.length;
        if (e.key === "ArrowLeft") j = (i - 1 + tabs.length) % tabs.length;
        if (e.key === "Home") j = 0;
        if (e.key === "End") j = tabs.length - 1;
        if (j !== null) { e.preventDefault(); tabs[j].focus(); select(tabs[j]); }
      });
    });
  });

  // terminal replay of a real /raftly session shape
  var body = document.getElementById("term-body");
  var script = [
    ["p", "> /raftly build a calculator app + website"],
    ["d", "  context: empty repo -> GREENFIELD"],
    ["", ""],
    ["b", "GREENFIELD · BLUEPRINT_COMPLETE"],
    ["", ""],
    ["", "[Head of Product Strategy]"],
    ["", "Consumer utility: correctness, speed, offline."],
    ["", "No accounts, sync or ads in V1."],
    ["", ""],
    ["", "Decisions"],
    ["g", "  ADR-001 Client-only, no backend      92"],
    ["g", "  ADR-003 Decimal: 0.1 + 0.2 = 0.3     90"],
    ["g", "  ADR-004 Expo + RN Web, one codebase  72"],
    ["g", "  ADR-005 Design B: live expression    75"],
    ["", ""],
    ["", "Build graph  7 nodes · 4 phases · 7 prompts"],
    ["", "Launch gate  16 apply · 29 not applicable"],
    ["d", "             no evidence yet -> no score"],
    ["", ""],
    ["p", "Next: /raftly build next  -> N001 engine"]
  ];
  function render(lines) {
    body.innerHTML = "";
    lines.forEach(function (l) {
      var span = document.createElement("span");
      if (l[0]) span.className = l[0];
      span.textContent = l[1] + "\n";
      body.appendChild(span);
    });
  }
  var timer = null;
  function play() {
    if (!body) return;
    clearTimeout(timer);
    if (reduce) { render(script); return; }
    body.innerHTML = "";
    var li = 0, ci = 0, span = null;
    var caret = document.createElement("span"); caret.className = "caret"; caret.setAttribute("aria-hidden", "true");
    function tick() {
      if (li >= script.length) { body.appendChild(caret); return; }
      var line = script[li];
      if (!span) { span = document.createElement("span"); if (line[0]) span.className = line[0]; body.appendChild(span); }
      var typing = li === 0;
      if (typing && ci < line[1].length) {
        span.textContent += line[1][ci++]; body.appendChild(caret);
        timer = setTimeout(tick, 28);
      } else {
        span.textContent = line[1] + "\n"; li++; ci = 0; span = null;
        timer = setTimeout(tick, li === 1 ? 500 : 140);
      }
    }
    tick();
  }
  if (body) {
    render(script); // full transcript is in the DOM for screen readers and no-JS
    var replay = document.getElementById("term-replay");
    if (replay) replay.addEventListener("click", play);
    if ("IntersectionObserver" in window && !reduce) {
      var started = false;
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting && !started) { started = true; play(); obs.disconnect(); }
      }, { threshold: 0.3 }).observe(body);
    }
  }

  // reveal on scroll
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
})();
