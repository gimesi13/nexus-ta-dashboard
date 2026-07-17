(function () {
  "use strict";

  var TYPE_COLORS = {
    Validation: "#a8894a",
    CRUD: "#6a7a94",
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

  function renderAreas(list, total) {
    var host = document.getElementById("area-bars");
    var meta = document.getElementById("area-meta");
    if (!host) return;
    meta.textContent = list.length + " domains";
    var max = list[0] ? list[0].count : 1;
    host.innerHTML = list.map(function (a, i) {
      var pct = total ? Math.round((a.count / total) * 1000) / 10 : 0;
      var width = Math.max(4, Math.round((a.count / max) * 100));
      return '<div class="ov-bar-row" style="--i:' + i + '">' +
        '<div class="ov-bar-label" title="' + esc(a.name) + '">' + esc(a.name) + "</div>" +
        '<div class="ov-bar-track"><div class="ov-bar-fill" style="--w:' + width + '%"></div></div>' +
        '<div class="ov-bar-count">' + a.count + '<span>' + pct + "%</span></div>" +
        "</div>";
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
      return '<div class="ov-type-row" style="--i:' + i + '; --c:' + color + '">' +
        '<div class="ov-type-top">' +
          '<span class="ov-type-name">' + esc(t.name) + "</span>" +
          '<span class="ov-type-pct">' + pct + "%</span>" +
        "</div>" +
        '<div class="ov-type-track"><div class="ov-type-fill" style="width:' + pct + '%"></div></div>' +
        '<div class="ov-type-count">' + t.count + " tests</div>" +
        "</div>";
    }).join("");
    requestAnimationFrame(function () {
      host.classList.add("ready");
    });
  }

  function renderTags(list) {
    var host = document.getElementById("tag-cloud");
    if (!host) return;
    host.innerHTML = list.slice(0, 10).map(function (t) {
      return '<a class="ov-tag" href="inventory.html">' + esc(t.name) +
        '<span>' + t.count + "</span></a>";
    }).join("");
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
      meta.textContent = "Not published yet";
      body.innerHTML = '<div class="ov-empty">' +
        esc((d && d.message) || "Nightly results unavailable.") +
        "</div>";
      return;
    }

    var s = d.summary;
    var build = d.build || {};
    var status = (build.status || "").toUpperCase();
    var statusCls = status === "SUCCESS" ? "ok" : (status === "FAILURE" || status === "ERROR" ? "bad" : "mid");
    meta.textContent = (build.number ? "#" + build.number + " · " : "") +
      "generated " + (d.generatedAt || "—");

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
          return '<li title="' + esc(f.id) + '"><code>' + esc(f.name || f.id) +
            "</code>" +
            (f.message ? '<span class="ov-nightly-msg">' + esc(f.message) + "</span>" : "") +
            "</li>";
        }).join("") +
        "</ul>" +
        (d.failedTruncated
          ? '<p class="ov-nightly-more">+' + d.failedTruncated + " more — see TeamCity</p>"
          : "");
    }

    var trend = d.trend || [];
    var trendBits = trend.slice(-7).map(function (t) {
      return '<span class="ov-nightly-trend-pt" title="' +
        esc((t.date || "") + " · " + (t.passRate != null ? t.passRate + "%" : "")) +
        '">' + esc(t.passRate != null ? String(Math.round(t.passRate)) : "—") + "</span>";
    }).join("");
    var trendRow = trendBits
      ? '<div class="ov-nightly-trend"><span class="ov-nightly-trend-label">Pass % (recent)</span>' +
        trendBits + "</div>"
      : "";

    body.innerHTML =
      '<div class="ov-nightly-top">' + statusChip + link + "</div>" +
      kpis + trendRow +
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

      renderAreas(agg.areas, total);
      renderTypes(agg.types, total);
      renderTags(agg.tags);

      document.querySelector(".ov-shell").classList.add("loaded");
    })
    .catch(function () {
      document.getElementById("gen-stamp").textContent = "Inventory data unavailable";
      ["area-bars", "type-mix"].forEach(function (id) {
        var el = document.getElementById(id);
        if (el) el.innerHTML = '<div class="ov-empty">Could not load inventory.json</div>';
      });
    });
})();
