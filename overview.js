(function () {
  "use strict";

  var TYPE_COLORS = {
    Validation: "#a8894a",
    CRUD: "#6a7a94",
    Query: "#5a8a7a",
    Workflow: "#7a7294",
    E2E: "#7a7294",
    Other: "#5a5a60",
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function countUp(el, target, duration) {
    var start = 0;
    var from = 0;
    var t0 = null;
    function frame(ts) {
      if (t0 == null) t0 = ts;
      var p = Math.min(1, (ts - t0) / duration);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(from + (target - from) * eased));
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function aggregate(rows) {
    var areas = {};
    var types = {};
    var tags = {};
    rows.forEach(function (r) {
      var n = r.cases || 1;
      areas[r.area] = (areas[r.area] || 0) + n;
      var t = r.type || "Other";
      types[t] = (types[t] || 0) + n;
      (r.tags || []).forEach(function (tag) {
        tags[tag] = (tags[tag] || 0) + 1;
      });
    });
    function sorted(obj) {
      return Object.keys(obj)
        .map(function (k) { return { name: k, count: obj[k] }; })
        .sort(function (a, b) { return b.count - a.count; });
    }
    return { areas: sorted(areas), types: sorted(types), tags: sorted(tags) };
  }

  function renderSuiteMeta(total, areaCount) {
    var meta = document.getElementById("suite-meta");
    if (!meta) return;
    meta.innerHTML =
      esc(String(total)) + " tests · " + esc(String(areaCount)) + " domains · " +
      '<a class="ov-nightly-link" href="inventory.html">Inventory →</a>';
  }

  function renderAreas(list, total) {
    var host = document.getElementById("area-bars");
    var meta = document.getElementById("area-meta");
    if (!host) return;
    var top = list.slice(0, 8);
    if (meta) {
      meta.textContent = top.length + " of " + list.length;
    }
    var max = top[0] ? top[0].count : 1;
    host.innerHTML = top.map(function (a, i) {
      var pct = total ? Math.round((a.count / total) * 1000) / 10 : 0;
      var width = Math.max(4, Math.round((a.count / max) * 100));
      var href = "inventory.html?area=" + encodeURIComponent(a.name);
      return '<a class="ov-suite-area" href="' + esc(href) + '" style="--i:' + i +
        '" title="Open ' + esc(a.name) + ' in inventory">' +
        '<span class="ov-suite-area-name">' + esc(a.name) + "</span>" +
        '<span class="ov-suite-area-track"><span class="ov-suite-area-fill" style="--w:' +
          width + '%"></span></span>' +
        '<span class="ov-suite-area-count">' + a.count +
          '<span>' + pct + "%</span></span>" +
        "</a>";
    }).join("");
    requestAnimationFrame(function () {
      host.classList.add("ready");
    });
  }

  function renderTypes(list, total) {
    var host = document.getElementById("type-mix");
    if (!host) return;
    host.innerHTML = list.map(function (t, i) {
      var pct = total ? Math.round((t.count / total) * 1000) / 10 : 0;
      var color = TYPE_COLORS[t.name] || TYPE_COLORS.Other;
      var href = "inventory.html?type=" + encodeURIComponent(t.name);
      return '<a class="ov-suite-type" href="' + esc(href) + '" style="--i:' + i +
        '; --c:' + color + '" title="Open ' + esc(t.name) + ' tests in inventory">' +
        '<span class="ov-suite-type-num">' + pct + "%</span>" +
        '<span class="ov-suite-type-label">' + esc(t.name) + "</span>" +
        '<span class="ov-suite-type-count">' + t.count + " tests</span>" +
        "</a>";
    }).join("");
    requestAnimationFrame(function () {
      host.classList.add("ready");
    });
  }

  function renderCoverage(d) {
    var meta = document.getElementById("coverage-meta");
    var body = document.getElementById("coverage-body");
    if (!meta || !body) return;

    if (!d || !d.summary) {
      meta.textContent = "Not published yet";
      body.innerHTML = '<div class="ov-empty">' +
        esc((d && d.message) || "Coverage data unavailable.") + "</div>";
      return;
    }

    var s = d.summary;
    meta.innerHTML =
      "generated " + esc(d.generatedAt || "—") +
      ' · <a class="ov-nightly-link" href="coverage.html">Open coverage →</a>';

    var queue = (d.queue || []).slice(0, 5);
    var gapsHtml;
    if (!queue.length) {
      gapsHtml = '<p class="ov-nightly-none">No open gaps in the backlog.</p>';
    } else {
      gapsHtml =
        '<ul class="ov-cov-gaps">' +
        queue.map(function (row) {
          var q = row.operationId || row.p || "";
          var href = "coverage.html?tab=queue&q=" + encodeURIComponent(q);
          return '<li>' +
            '<a class="ov-cov-gap" href="' + esc(href) + '">' +
              '<span class="ov-cov-gap-method">' + esc(row.m || "") + "</span>" +
              '<span class="ov-cov-gap-path">' + esc(row.p || "") + "</span>" +
              '<span class="ov-cov-gap-meta">' +
                esc(row.category || "") +
                (row.riskBand ? " · " + esc(row.riskBand) : "") +
                (row.gap === "new" ? " · brand-new" : "") +
              "</span>" +
            "</a>" +
            "</li>";
        }).join("") +
        "</ul>";
    }

    body.innerHTML =
      '<div class="ov-cov-kpis">' +
        '<a class="ov-cov-kpi" href="coverage.html?tab=quality" title="How coverage is counted">' +
          '<span class="ov-cov-kpi-num">' + esc(String(s.coveragePercent)) + "%</span>" +
          '<span class="ov-cov-kpi-label">Coverage</span>' +
        "</a>" +
        '<a class="ov-cov-kpi" href="coverage.html?tab=domain&status=tested" title="Browse tested endpoints">' +
          '<span class="ov-cov-kpi-num ov-nightly-ok">' + esc(String(s.tested)) + "</span>" +
          '<span class="ov-cov-kpi-label">Tested</span>' +
        "</a>" +
        '<a class="ov-cov-kpi" href="coverage.html?tab=queue" title="Open the gap work queue">' +
          '<span class="ov-cov-kpi-num">' + esc(String(s.untested)) + "</span>" +
          '<span class="ov-cov-kpi-label">Gaps</span>' +
        "</a>" +
        '<a class="ov-cov-kpi ov-cov-kpi-warn" href="coverage.html?tab=queue&risk=high" title="High-risk gaps only">' +
          '<span class="ov-cov-kpi-num">' + esc(String(s.highRiskGaps)) + "</span>" +
          '<span class="ov-cov-kpi-label">High-risk</span>' +
        "</a>" +
        '<a class="ov-cov-kpi" href="coverage.html?tab=queue&gap=new" title="Brand-new OpenAPI gaps only">' +
          '<span class="ov-cov-kpi-num">' + esc(String(s.brandNew)) + "</span>" +
          '<span class="ov-cov-kpi-label">Brand-new</span>' +
        "</a>" +
      "</div>" +
      '<div class="ov-nightly-fail-head ov-cov-gap-head">Top backlog gaps ' +
        '<span class="ov-panel-meta">' +
          '<a class="ov-nightly-link" href="coverage.html?tab=queue">Full queue →</a>' +
        "</span></div>" +
      gapsHtml;
  }

  function fmtDuration(sec) {
    if (sec == null || isNaN(sec)) return "—";
    if (sec < 90) return Math.round(sec) + "s";
    var m = Math.floor(sec / 60);
    var s = Math.round(sec % 60);
    if (m < 90) return m + "m " + s + "s";
    var h = Math.floor(m / 60);
    return h + "h " + (m % 60) + "m";
  }

  function renderNightly(d) {
    var meta = document.getElementById("nightly-meta");
    var body = document.getElementById("nightly-body");
    if (!meta || !body) return;

    if (!d || !d.available || !d.summary) {
      meta.innerHTML =
        'Not published yet · <a class="ov-nightly-link" href="nightly.html">Open Nightly Run →</a>';
      body.innerHTML = '<div class="ov-empty">' +
        esc((d && d.message) || "Nightly results unavailable.") +
        "</div>";
      return;
    }

    var s = d.summary;
    var build = d.build || {};
    var status = (build.status || "").toUpperCase();
    var statusCls = status === "SUCCESS" ? "ok" : (status === "FAILURE" || status === "ERROR" ? "bad" : "mid");
    meta.innerHTML =
      (build.number ? "#" + esc(build.number) + " · " : "") +
      "generated " + esc(d.generatedAt || "—") +
      ' · <a class="ov-nightly-link" href="nightly.html">Open Nightly Run →</a>';

    var kpis =
      '<div class="ov-nightly-kpis">' +
        '<div class="ov-nightly-kpi">' +
          '<div class="ov-nightly-kpi-num">' + esc(String(s.passRate)) + "%</div>" +
          '<div class="ov-nightly-kpi-label">Pass rate</div>' +
        "</div>" +
        '<div class="ov-nightly-kpi">' +
          '<div class="ov-nightly-kpi-num ov-nightly-ok">' + esc(String(s.passed)) + "</div>" +
          '<div class="ov-nightly-kpi-label">Passed</div>' +
        "</div>" +
        '<div class="ov-nightly-kpi">' +
          '<div class="ov-nightly-kpi-num ov-nightly-bad">' +
            esc(String((s.failures || 0) + (s.errors || 0))) + "</div>" +
          '<div class="ov-nightly-kpi-label">Failed</div>' +
        "</div>" +
        '<div class="ov-nightly-kpi">' +
          '<div class="ov-nightly-kpi-num">' + esc(String(s.skipped || 0)) + "</div>" +
          '<div class="ov-nightly-kpi-label">Skipped</div>' +
        "</div>" +
        '<div class="ov-nightly-kpi">' +
          '<div class="ov-nightly-kpi-num">' + esc(fmtDuration(s.timeSec)) + "</div>" +
          '<div class="ov-nightly-kpi-label">Duration</div>' +
        "</div>" +
      "</div>";

    var link = build.webUrl
      ? '<a class="ov-nightly-link" href="' + esc(build.webUrl) +
        '" target="_blank" rel="noopener">Open build in TeamCity →</a>'
      : "";

    var statusChip = status
      ? '<span class="ov-nightly-status ' + statusCls + '">' + esc(status) + "</span>"
      : "";

    var failed = d.failed || [];
    var failBlock;
    if (!failed.length) {
      failBlock = '<p class="ov-nightly-none">No failing tests in this run.</p>';
    } else {
      failBlock =
        '<ul class="ov-nightly-fails">' +
        failed.map(function (f) {
          var href = f.inventoryHref ||
            ("inventory.html?q=" + encodeURIComponent(f.name || ""));
          if (href.indexOf("run=") === -1) {
            href += (href.indexOf("?") >= 0 ? "&" : "?") + "run=failed";
          }
          var badge = f.newFailure
            ? '<span class="ny-fail-badge" title="Did not fail in the previous build">New</span>'
            : "";
          return '<li>' +
            '<a class="ny-fail-link" href="' + esc(href) + '" title="' + esc(f.id || "") + '">' +
              '<span class="ny-fail-name-row">' +
                '<span class="ny-fail-name">' + esc(f.name || f.id) + "</span>" +
                badge +
              "</span>" +
              '<span class="ny-fail-go">Open in inventory →</span>' +
            "</a>" +
            "</li>";
        }).join("") +
        "</ul>" +
        (d.failedTruncated
          ? '<p class="ov-nightly-more">+' + d.failedTruncated + " more — see TeamCity</p>"
          : "");
    }

    var nut = d.nutshell || {};
    var nutBlock = "";
    if (nut.headline) {
      var tone = (nut.tone || "ok").toLowerCase();
      if (tone !== "ok" && tone !== "warn" && tone !== "bad") tone = "ok";
      nutBlock =
        '<div class="ny-nutshell ny-nutshell-compact ny-nutshell-' + tone + '">' +
          '<div class="ny-nutshell-label">In a nutshell</div>' +
          '<div class="ny-nutshell-headline">' + esc(nut.headline) + "</div>" +
          (nut.investigation
            ? '<p class="ny-nutshell-body">' + esc(nut.investigation) + "</p>"
            : "") +
        "</div>";
    }

    body.innerHTML =
      '<div class="ov-nightly-top">' + statusChip + link + "</div>" +
      nutBlock +
      kpis +
      '<div class="ov-nightly-fail-head">Failures</div>' +
      failBlock;
  }

  fetch("data/nightly.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(renderNightly)
    .catch(function () {
      renderNightly({ available: false, message: "Could not load nightly.json" });
    });

  fetch("data/inventory.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function (d) {
      var rows = d.rows || [];
      var agg = aggregate(rows);
      var total = d.cases || 0;

      document.getElementById("kpi-methods").textContent =
        (d.features || 0) + " feature method" + (d.features === 1 ? "" : "s");
      document.getElementById("gen-stamp").textContent =
        "Generated " + d.generatedAt + " · parsed from " + d.source;

      countUp(document.getElementById("kpi-cases"), d.cases || 0, 900);
      countUp(document.getElementById("kpi-specs"), d.specs || 0, 900);
      countUp(document.getElementById("kpi-areas"), d.areas || 0, 900);
      countUp(document.getElementById("kpi-features"), d.features || 0, 900);

      renderSuiteMeta(total, agg.areas.length);
      renderTypes(agg.types, total);
      renderAreas(agg.areas, total);

      showOverview();
    })
    .catch(function () {
      document.getElementById("gen-stamp").textContent = "Inventory data unavailable";
      var suiteMeta = document.getElementById("suite-meta");
      if (suiteMeta) suiteMeta.textContent = "Unavailable";
      ["area-bars", "type-mix"].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = '<div class="ov-empty">Could not load inventory.json</div>';
      });
      showOverview();
    });

  fetch("data/coverage.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(renderCoverage)
    .catch(function () {
      renderCoverage({ message: "Could not load coverage.json" });
    });

  function showOverview() {
    var shell = document.querySelector(".ov-shell");
    if (shell) shell.classList.add("loaded");
  }
})();
