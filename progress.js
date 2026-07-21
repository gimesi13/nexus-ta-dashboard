(function () {
  "use strict";

  var WINDOW_LABELS = {
    "7d": "Last 7 days",
    "14d": "Last 14 days",
    "30d": "Last 30 days",
    "90d": "Last 90 days",
  };
  var TYPE_CLS = {
    CRUD: "is-crud",
    Validation: "is-val",
    Workflow: "is-flow",
    Query: "is-query",
    E2E: "is-e2e",
    Other: "is-other",
  };

  var state = {
    data: null,
    window: "90d",
    q: "",
  };

  var els = {
    windows: document.getElementById("windows"),
    summary: document.getElementById("summary"),
    weeks: document.getElementById("weeks"),
    additions: document.getElementById("additions"),
    tickets: document.getElementById("tickets"),
    areas: document.getElementById("areas"),
    search: document.getElementById("add-search"),
    provenance: document.getElementById("provenance"),
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function fmtDelta(n, suffix) {
    if (n == null || isNaN(n)) return "—";
    var v = Number(n);
    var sign = v > 0 ? "+" : "";
    return sign + v + (suffix || "");
  }

  function currentWindow() {
    return (state.data && state.data.windows && state.data.windows[state.window]) || null;
  }

  function renderWindows() {
    if (!els.windows || !state.data) return;
    var keys = Object.keys(WINDOW_LABELS).filter(function (k) {
      return state.data.windows && state.data.windows[k];
    });
    els.windows.innerHTML = keys.map(function (k) {
      var w = state.data.windows[k];
      var on = k === state.window;
      return (
        '<button type="button" class="prog-win' + (on ? " active" : "") +
          '" data-window="' + esc(k) + '" role="tab" aria-selected="' + (on ? "true" : "false") + '">' +
          '<span class="prog-win-label">' + esc(WINDOW_LABELS[k]) + "</span>" +
          '<span class="prog-win-num">+' + esc(w.featuresAdded) + "</span>" +
        "</button>"
      );
    }).join("");
  }

  function typeBar(byType) {
    var segs = Object.keys(TYPE_CLS).filter(function (t) { return byType && byType[t]; }).map(function (t) {
      return { label: t, value: byType[t], cls: TYPE_CLS[t] };
    });
    var total = segs.reduce(function (n, s) { return n + s.value; }, 0) || 1;
    var bars = segs.map(function (seg) {
      var pct = Math.max(0.6, (seg.value / total) * 100);
      return (
        '<span class="inv-stack-seg ' + seg.cls + '" style="width:' + pct + '%" ' +
          'title="' + esc(seg.label) + ": +" + esc(seg.value) + '"></span>'
      );
    }).join("");
    var legend = segs.map(function (seg) {
      return (
        '<span class="inv-stack-key">' +
          '<span class="inv-stack-dot ' + seg.cls + '"></span>' +
          '<strong>+' + esc(seg.value) + "</strong> " + esc(seg.label) +
        "</span>"
      );
    }).join("");
    if (!segs.length) {
      return '<div class="prog-empty-inline">No new features in this window.</div>';
    }
    return (
      '<div class="inv-stack" role="img" aria-label="Added features by type">' + bars + "</div>" +
      '<div class="inv-stack-keys">' + legend + "</div>"
    );
  }

  function coverageChip(data) {
    var cov = data.coverage || {};
    var d = cov.delta14d || {};
    var cur = cov.currentPercent != null ? cov.currentPercent + "%" : "—";
    var delta = d.deltaPoints;
    var deltaHtml =
      delta == null
        ? '<span class="prog-cov-note">' + esc(d.note || "Coverage trend builds after a few publishes.") + "</span>"
        : '<span class="prog-cov-delta">' + esc(fmtDelta(delta, " pts")) +
          ' vs ' + esc(d.priorDate) + "</span>";
    return (
      '<div class="prog-cov">' +
        '<div class="prog-cov-num">' + esc(cur) + "</div>" +
        '<div class="prog-cov-copy">' +
          '<div class="prog-cov-label">Endpoint coverage</div>' +
          deltaHtml +
        "</div>" +
      "</div>"
    );
  }

  function renderSummary() {
    var w = currentWindow();
    if (!els.summary || !w || !state.data) return;
    els.summary.innerHTML =
      '<div class="prog-bar-hero">' +
        '<div class="prog-bar-hero-top">' +
          '<div class="prog-bar-pct">+' + esc(w.featuresAdded) + "</div>" +
          '<div class="prog-bar-copy">' +
            '<div class="prog-bar-title">features added · +' + esc(w.casesAdded) +
              " cases</div>" +
            '<div class="prog-bar-sub">' +
              esc(WINDOW_LABELS[state.window]) + " · " +
              esc(w.from) + " → " + esc(w.to) + " · " +
              esc(w.areasTouched) + " areas · " +
              esc(w.ticketsTouched) + " tickets" +
            "</div>" +
          "</div>" +
          coverageChip(state.data) +
        "</div>" +
        typeBar(w.byType) +
      "</div>";
  }

  function renderWeeks() {
    if (!els.weeks || !state.data) return;
    var weeks = state.data.weeks || [];
    var max = Math.max(1, weeks.reduce(function (n, w) {
      return Math.max(n, w.featuresAdded || 0);
    }, 0));
    els.weeks.innerHTML =
      '<div class="prog-weeks-head">' +
        '<h2 class="prog-panel-title">Weekly pace</h2>' +
        '<span class="prog-weeks-hint">Features first seen in git · last 12 weeks</span>' +
      "</div>" +
      '<div class="prog-week-chart" role="img" aria-label="Weekly feature additions">' +
        weeks.map(function (w) {
          var h = Math.max(w.featuresAdded ? 8 : 2, Math.round((w.featuresAdded / max) * 64));
          return (
            '<div class="prog-week-col" title="' + esc(w.weekStart) + ": +" +
              esc(w.featuresAdded) + ' features">' +
              '<div class="prog-week-bar" style="height:' + h + 'px"></div>' +
              '<div class="prog-week-n">' + (w.featuresAdded ? "+" + esc(w.featuresAdded) : "") + "</div>" +
              '<div class="prog-week-d">' + esc(String(w.weekStart).slice(5)) + "</div>" +
            "</div>"
          );
        }).join("") +
      "</div>";
  }

  function filteredAdditions(w) {
    var q = state.q.trim().toLowerCase();
    var rows = w.additions || [];
    if (!q) return rows;
    return rows.filter(function (a) {
      var blob = [
        a.name, a.area, a.spec, a.type, a.subject,
        (a.tickets || []).join(" "), (a.tags || []).join(" "),
      ].join(" ").toLowerCase();
      return blob.indexOf(q) >= 0;
    });
  }

  function renderAdditions() {
    var w = currentWindow();
    if (!els.additions || !w) return;
    var rows = filteredAdditions(w);
    if (!rows.length) {
      els.additions.innerHTML = '<div class="prog-empty">No additions match.</div>';
      return;
    }
    els.additions.innerHTML =
      '<ul class="prog-add-list">' +
        rows.map(function (a) {
          var tickets = (a.tickets || []).map(function (t) {
            return '<span class="prog-ticket">' + esc(t) + "</span>";
          }).join("");
          return (
            '<li class="prog-add">' +
              '<a class="prog-add-link" href="' + esc(a.inventoryHref || "inventory.html") + '">' +
                '<div class="prog-add-top">' +
                  '<span class="prog-add-date">' + esc(a.date) + "</span>" +
                  '<span class="prog-add-area">' + esc(a.area || "—") + "</span>" +
                  (a.type ? '<span class="prog-add-type">' + esc(a.type) + "</span>" : "") +
                  (a.cases > 1 ? '<span class="prog-add-cases">' + esc(a.cases) + " cases</span>" : "") +
                  (a.gone ? '<span class="prog-add-gone">removed since</span>' : "") +
                "</div>" +
                '<div class="prog-add-name">' + esc(a.name) + "</div>" +
                '<div class="prog-add-meta">' +
                  tickets +
                  (a.spec ? '<span class="prog-add-spec">' + esc(a.spec) + "</span>" : "") +
                "</div>" +
              "</a>" +
            "</li>"
          );
        }).join("") +
      "</ul>";
  }

  function renderTickets() {
    var w = currentWindow();
    if (!els.tickets || !w) return;
    var list = w.tickets || [];
    if (!list.length) {
      els.tickets.innerHTML = '<div class="prog-empty">No ticket keys in commit subjects.</div>';
      return;
    }
    els.tickets.innerHTML =
      '<ul class="prog-rank">' +
        list.map(function (t) {
          return (
            '<li>' +
              '<span class="prog-rank-key">' + esc(t.key) + "</span>" +
              '<span class="prog-rank-val">+' + esc(t.featuresAdded) +
                (t.casesAdded !== t.featuresAdded ? " · +" + esc(t.casesAdded) + " cases" : "") +
              "</span>" +
            "</li>"
          );
        }).join("") +
      "</ul>";
  }

  function renderAreas() {
    var w = currentWindow();
    if (!els.areas || !w) return;
    var list = w.byArea || [];
    if (!list.length) {
      els.areas.innerHTML = '<div class="prog-empty">No areas touched.</div>';
      return;
    }
    els.areas.innerHTML =
      '<ul class="prog-rank">' +
        list.map(function (a) {
          return (
            '<li>' +
              '<span class="prog-rank-key">' + esc(a.area) + "</span>" +
              '<span class="prog-rank-val">+' + esc(a.featuresAdded) + "</span>" +
            "</li>"
          );
        }).join("") +
      "</ul>";
  }

  function renderAll() {
    renderWindows();
    renderSummary();
    renderWeeks();
    renderAdditions();
    renderTickets();
    renderAreas();
    if (els.provenance && state.data) {
      els.provenance.textContent =
        (state.data.methodology || "") +
        " Generated " + (state.data.generatedAt || "—") +
        " · scan since " + (state.data.since || "—") + ".";
    }
  }

  function wire() {
    if (els.windows) {
      els.windows.addEventListener("click", function (e) {
        var btn = e.target.closest("[data-window]");
        if (!btn) return;
        var w = btn.getAttribute("data-window");
        if (!w || w === state.window) return;
        state.window = w;
        renderAll();
      });
    }
    if (els.search) {
      els.search.addEventListener("input", function () {
        state.q = els.search.value || "";
        renderAdditions();
      });
    }
  }

  wire();

  fetch("data/progress.json", { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then(function (data) {
      state.data = data;
      state.window = data.defaultWindow || "90d";
      renderAll();
    })
    .catch(function (err) {
      if (els.summary) {
        els.summary.innerHTML =
          '<p class="prog-lead">Failed to load progress: ' + esc(err.message) + "</p>";
      }
    });
})();
