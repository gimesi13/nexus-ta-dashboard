(function () {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function statusClass(status) {
    var s = (status || "").toLowerCase();
    if (s === "live") return "aip-status-live";
    if (s === "active") return "aip-status-active";
    if (s === "prototype") return "aip-status-proto";
    return "";
  }

  function kpisHtml(stats) {
    if (!stats || !stats.length) return "";
    return '<div class="aip-kpis">' +
      stats.map(function (k) {
        return '<div class="aip-kpi">' +
          '<div class="aip-kpi-num">' + esc(k.value) + "</div>" +
          '<div class="aip-kpi-label">' + esc(k.label) + "</div>" +
          (k.hint ? '<div class="aip-kpi-hint">' + esc(k.hint) + "</div>" : "") +
          "</div>";
      }).join("") +
      "</div>";
  }

  function tagsHtml(tags) {
    if (!tags || !tags.length) return "";
    return '<div class="aip-tags">' +
      tags.map(function (t) { return '<span class="aip-tag">' + esc(t) + "</span>"; }).join("") +
      "</div>";
  }

  function itemHtml(it) {
    return '<article class="aip-item">' +
      '<div class="aip-item-head">' +
        '<span class="aip-item-name">' + esc(it.name) + "</span>" +
        '<span class="aip-badges">' +
          (it.scope ? '<span class="aip-scope">' + esc(it.scope) + "</span>" : "") +
          (it.status
            ? '<span class="aip-status ' + statusClass(it.status) + '">' + esc(it.status) + "</span>"
            : "") +
        "</span>" +
      "</div>" +
      '<p class="aip-item-sum">' + esc(it.summary) + "</p>" +
      tagsHtml(it.tags) +
      "</article>";
  }

  function catHtml(cat, idx) {
    var items = (cat.items || []).map(itemHtml).join("");
    return '<section class="aip-cat" id="' + esc(cat.id || ("cat-" + idx)) + '">' +
      '<div class="aip-cat-head">' +
        '<span class="aip-cat-index">' + (idx < 9 ? "0" : "") + (idx + 1) + "</span>" +
        '<div class="aip-cat-heads">' +
          '<h2 class="aip-cat-title">' + esc(cat.title) +
            ' <span class="aip-cat-count">' + (cat.items || []).length + "</span></h2>" +
          (cat.role ? '<p class="aip-cat-role">' + esc(cat.role) + "</p>" : "") +
        "</div>" +
      "</div>" +
      '<div class="aip-items">' + items + "</div>" +
      "</section>";
  }

  function showShell() {
    var shell = document.querySelector(".ov-shell");
    if (shell) shell.classList.add("loaded");
  }

  function render(d) {
    var meta = document.getElementById("aip-meta");
    var body = document.getElementById("aip-body");
    var prov = document.getElementById("provenance");

    if (!d || !d.categories) {
      if (meta) meta.textContent = "Unavailable";
      if (body) body.innerHTML = '<div class="ov-empty">Could not load data/ai-platform.json</div>';
      showShell();
      return;
    }

    if (meta) meta.textContent = "updated " + (d.generatedAt || "\u2014");

    body.innerHTML =
      (d.intro ? '<p class="aip-intro">' + esc(d.intro) + "</p>" : "") +
      kpisHtml(d.stats) +
      '<div class="aip-cats">' +
        d.categories.map(catHtml).join("") +
      "</div>";

    if (prov) {
      prov.textContent =
        "A living inventory of AI-platform work across the monorepo \u00b7 owner " +
        (d.owner || "\u2014") + " \u00b7 updated " + (d.generatedAt || "\u2014");
    }
    showShell();
  }

  fetch("data/ai-platform.json", { cache: "no-cache" })
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(render)
    .catch(function () { render(null); });
})();
