(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmtDuration(sec) {
    if (sec == null || isNaN(sec)) return "—";
    sec = Math.round(Number(sec));
    if (sec < 90) return sec + "s";
    var m = Math.floor(sec / 60);
    var s = sec % 60;
    if (m < 90) return m + "m " + s + "s";
    var h = Math.floor(m / 60);
    return h + "h " + (m % 60) + "m";
  }

  function fmtTcDate(raw) {
    if (!raw || raw.length < 15) return "—";
    return raw.slice(0, 4) + "-" + raw.slice(4, 6) + "-" + raw.slice(6, 8) +
      " " + raw.slice(9, 11) + ":" + raw.slice(11, 13) + " UTC";
  }

  function statusClass(status) {
    var s = (status || "").toUpperCase();
    if (s === "SUCCESS") return "ok";
    if (s === "FAILURE" || s === "ERROR") return "bad";
    return "mid";
  }

  function fmtMs(ms) {
    if (ms == null || isNaN(ms)) return "";
    var sec = Math.round(Number(ms) / 1000);
    if (sec < 60) return sec + "s";
    return Math.floor(sec / 60) + "m " + (sec % 60) + "s";
  }

  function failInventoryHref(f) {
    var href = f.inventoryHref ||
      ("inventory.html?q=" + encodeURIComponent(f.name || ""));
    if (href.indexOf("run=") === -1) {
      href += (href.indexOf("?") >= 0 ? "&" : "?") + "run=failed";
    }
    return href;
  }

  function failItemsHtml(failed, truncated) {
    if (!failed.length) {
      return '<p class="ov-nightly-none">No active (non-muted) failures in this run.</p>';
    }
    return '<ul class="ov-nightly-fails">' +
      failed.map(function (f) {
        var href = failInventoryHref(f);
        var meta = [];
        if (f.area) meta.push(f.area);
        if (f.spec) meta.push(f.spec);
        var dur = fmtMs(f.durationMs);
        var badge = f.newFailure
          ? '<span class="ny-fail-badge" title="Did not fail in the previous build">New</span>'
          : "";
        return '<li>' +
          '<a class="ny-fail-link" href="' + esc(href) + '">' +
            '<span class="ny-fail-name-row">' +
              '<span class="ny-fail-name">' + esc(f.name || f.id) + "</span>" +
              badge +
            "</span>" +
            '<span class="ny-fail-meta">' +
              (meta.length ? '<span class="ny-fail-class">' + esc(meta.join(" · ")) + "</span>" : "") +
              (dur ? '<span class="ny-fail-class">' + esc(dur) + "</span>" : "") +
            "</span>" +
            '<span class="ny-fail-go">Open in inventory →</span>' +
          "</a>" +
          "</li>";
      }).join("") +
      "</ul>" +
      (truncated
        ? '<p class="ov-nightly-more">+' + truncated + " more — see TeamCity</p>"
        : "");
  }

  function showShell() {
    var shell = document.querySelector(".ov-shell");
    if (shell) shell.classList.add("loaded");
  }

  function render(d) {
    var meta = document.getElementById("nightly-meta");
    var body = document.getElementById("nightly-body");
    var prov = document.getElementById("provenance");

    if (!d || !d.available || !d.summary) {
      meta.textContent = "Not published yet";
      body.innerHTML = '<div class="ov-empty">' +
        esc((d && d.message) || "Nightly results unavailable.") + "</div>";
      if (prov) prov.textContent = "";
      showShell();
      return;
    }

    var s = d.summary;
    var build = d.build || {};
    var status = (build.status || "").toUpperCase();
    var statusCls = statusClass(status);

    meta.textContent = (build.number ? "#" + build.number + " · " : "") +
      "generated " + (d.generatedAt || "—");

    var buildsLink = document.getElementById("tc-builds-link");
    if (buildsLink && build.buildsUrl) buildsLink.href = build.buildsUrl;

    var link = build.webUrl
      ? '<a class="ov-nightly-link" href="' + esc(build.webUrl) +
        '" target="_blank" rel="noopener">Open build in TeamCity →</a>'
      : "";

    var statusChip = status
      ? '<span class="ov-nightly-status ' + statusCls + '">' + esc(status) + "</span>"
      : "";

    body.innerHTML =
      '<div class="ov-nightly-top">' + statusChip + link + "</div>" +
      '<div class="ov-nightly-kpis ov-nightly-kpis-6">' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num">' + esc(String(s.passRate)) +
          '%</div><div class="ov-nightly-kpi-label">Pass rate</div></div>' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num ov-nightly-ok">' + esc(String(s.passed)) +
          '</div><div class="ov-nightly-kpi-label">Passed</div></div>' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num ov-nightly-bad">' +
          esc(String((s.failures || 0) + (s.errors || 0))) +
          '</div><div class="ov-nightly-kpi-label">Failed</div></div>' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num">' + esc(String(s.newFailed != null ? s.newFailed : "—")) +
          '</div><div class="ov-nightly-kpi-label">New failed</div></div>' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num">' + esc(String(s.muted != null ? s.muted : "—")) +
          '</div><div class="ov-nightly-kpi-label">Muted</div></div>' +
        '<div class="ov-nightly-kpi"><div class="ov-nightly-kpi-num">' + esc(String(s.skipped != null ? s.skipped : "—")) +
          '</div><div class="ov-nightly-kpi-label">Ignored</div></div>' +
      "</div>" +
      '<dl class="ny-meta ny-meta-inline">' +
        "<div><dt>Build</dt><dd>" + esc(build.number || "—") + "</dd></div>" +
        "<div><dt>Duration</dt><dd>" + esc(fmtDuration(s.timeSec)) + "</dd></div>" +
        "<div><dt>Started</dt><dd>" + esc(fmtTcDate(build.startDate)) + "</dd></div>" +
        "<div><dt>Finished</dt><dd>" + esc(fmtTcDate(build.finishDate)) + "</dd></div>" +
        "<div><dt>Tests</dt><dd>" + esc(String(s.tests)) + "</dd></div>" +
        "<div><dt>Branch</dt><dd>" + esc(build.branchName || "—") + "</dd></div>" +
      "</dl>" +
      (build.statusText
        ? '<p class="ny-status-text">' + esc(build.statusText) + "</p>"
        : "") +
      '<div class="ov-nightly-fail-head">Failures <span class="ov-panel-meta">' +
        ((d.failed || []).length) + " non-muted" +
        ((d.failed || []).length
          ? ' · <a class="ov-nightly-link" href="inventory.html?run=failed">filter inventory</a>'
          : "") +
        "</span></div>" +
      failItemsHtml(d.failed || [], d.failedTruncated || 0);

    if (prov) {
      prov.textContent =
        "Generated " + (d.generatedAt || "—") +
        " · source " + (d.source || "—") +
        " · latest finished build on this TeamCity config";
    }
    showShell();
  }

  fetch("data/nightly.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(render)
    .catch(function () {
      render({ available: false, message: "Could not load data/nightly.json" });
    });
})();
