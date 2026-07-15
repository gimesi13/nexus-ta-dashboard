(function () {
  "use strict";

  var state = { rows: [], sortKey: "area", sortDir: 1 };

  var els = {
    kpis: document.getElementById("kpis"),
    search: document.getElementById("search"),
    area: document.getElementById("filter-area"),
    type: document.getElementById("filter-type"),
    tag: document.getElementById("filter-tag"),
    resultCount: document.getElementById("result-count"),
    rows: document.getElementById("rows"),
    provenance: document.getElementById("provenance"),
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function unique(rows, key) {
    var set = {};
    rows.forEach(function (r) {
      if (Array.isArray(r[key])) {
        r[key].forEach(function (v) { set[v] = true; });
      } else if (r[key]) {
        set[r[key]] = true;
      }
    });
    return Object.keys(set).sort();
  }

  function fillSelect(sel, values) {
    values.forEach(function (v) {
      var opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v;
      sel.appendChild(opt);
    });
  }

  function renderKpis(data) {
    var items = [
      { num: data.features, label: "Test cases" },
      { num: data.cases, label: "With parameters" },
      { num: data.specs, label: "Specs" },
      { num: data.areas, label: "Areas" },
    ];
    els.kpis.innerHTML = items.map(function (i) {
      return '<div class="kpi"><div class="kpi-num">' + i.num +
        '</div><div class="kpi-label">' + i.label + "</div></div>";
    }).join("");
  }

  function filtered() {
    var q = els.search.value.trim().toLowerCase();
    var area = els.area.value;
    var type = els.type.value;
    var tag = els.tag.value;
    return state.rows.filter(function (r) {
      if (area && r.area !== area) return false;
      if (type && r.type !== type) return false;
      if (tag && (r.tags || []).indexOf(tag) === -1) return false;
      if (q) {
        var hay = (r.name + " " + r.spec + " " + (r.tags || []).join(" ")).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function sortRows(rows) {
    var k = state.sortKey, dir = state.sortDir;
    return rows.slice().sort(function (a, b) {
      var av = a[k], bv = b[k];
      if (k === "cases") return (av - bv) * dir;
      return String(av).localeCompare(String(bv)) * dir;
    });
  }

  function typeBadge(t) {
    var cls = "type-badge type-" + esc(t).replace(/\s+/g, ".");
    return '<span class="' + cls + '">' + esc(t) + "</span>";
  }

  function tagLabels(tags) {
    if (!tags || !tags.length) return '<span class="cell-mono" style="opacity:.4">-</span>';
    return tags.map(function (t) { return '<span class="tag-label">' + esc(t) + "</span>"; }).join(" ");
  }

  function render() {
    var rows = sortRows(filtered());
    els.resultCount.textContent = rows.length + " of " + state.rows.length + " test cases";
    if (!rows.length) {
      els.rows.innerHTML = '<tr><td colspan="7" class="state-msg">No test cases match the filters.</td></tr>';
      return;
    }
    els.rows.innerHTML = rows.map(function (r) {
      return "<tr>" +
        "<td>" + esc(r.area) + "</td>" +
        '<td class="cell-spec">' + esc(r.spec) + "</td>" +
        '<td class="cell-name">' + esc(r.name) + "</td>" +
        "<td>" + typeBadge(r.type) + "</td>" +
        "<td>" + tagLabels(r.tags) + "</td>" +
        '<td class="cell-num">' + r.cases + "</td>" +
        "<td>" + esc(r.owner || "-") + "</td>" +
        "</tr>";
    }).join("");
  }

  function updateArrows() {
    document.querySelectorAll("th[data-sort]").forEach(function (th) {
      var arrow = th.querySelector(".arrow");
      if (th.getAttribute("data-sort") === state.sortKey) {
        arrow.textContent = state.sortDir === 1 ? "\u25B2" : "\u25BC";
      } else {
        arrow.textContent = "";
      }
    });
  }

  function wireEvents() {
    [els.search, els.area, els.type, els.tag].forEach(function (el) {
      el.addEventListener("input", render);
      el.addEventListener("change", render);
    });
    document.querySelectorAll("th[data-sort]").forEach(function (th) {
      th.addEventListener("click", function () {
        var key = th.getAttribute("data-sort");
        if (state.sortKey === key) {
          state.sortDir = -state.sortDir;
        } else {
          state.sortKey = key;
          state.sortDir = 1;
        }
        updateArrows();
        render();
      });
    });
  }

  fetch("data/inventory.json", { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then(function (data) {
      state.rows = data.rows || [];
      renderKpis(data);
      fillSelect(els.area, unique(state.rows, "area"));
      fillSelect(els.type, unique(state.rows, "type"));
      fillSelect(els.tag, unique(state.rows, "tags"));
      els.provenance.textContent =
        "Generated " + data.generatedAt + " from " + data.source +
        " (parsed directly from *TestSteps.groovy). Parameterized where: rows counted lower-bound.";
      wireEvents();
      updateArrows();
      render();
    })
    .catch(function (err) {
      els.rows.innerHTML =
        '<tr><td colspan="7" class="state-msg">Failed to load inventory: ' + esc(err.message) + "</td></tr>";
    });
})();
