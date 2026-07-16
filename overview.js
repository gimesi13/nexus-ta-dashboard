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
