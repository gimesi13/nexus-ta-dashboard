(function () {
  "use strict";

  var state = {
    data: null,
    tab: "queue",
    expanded: new Set(),
    copyTimer: null,
    copyGen: 0,
  };

  var els = {
    summary: document.getElementById("summary"),
    queueBody: document.getElementById("queue-body"),
    queueSearch: document.getElementById("queue-search"),
    queueGap: document.getElementById("queue-gap"),
    queueRisk: document.getElementById("queue-risk"),
    queueCount: document.getElementById("queue-count"),
    copyQueue: document.getElementById("copy-queue"),
    riskHint: document.getElementById("risk-hint"),
    domainSearch: document.getElementById("domain-search"),
    domainStatus: document.getElementById("domain-status"),
    domainCategory: document.getElementById("domain-category"),
    domainCount: document.getElementById("domain-count"),
    groups: document.getElementById("groups"),
    expandAll: document.getElementById("expand-all"),
    collapseAll: document.getElementById("collapse-all"),
    quality: document.getElementById("quality"),
    methodologyBody: document.getElementById("methodology-body"),
    provenance: document.getElementById("provenance"),
    tabs: document.querySelectorAll(".cov-tab"),
    panels: {
      queue: document.getElementById("panel-queue"),
      domain: document.getElementById("panel-domain"),
      quality: document.getElementById("panel-quality"),
    },
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function setTab(tab) {
    state.tab = tab;
    els.tabs.forEach(function (btn) {
      var on = btn.getAttribute("data-tab") === tab;
      btn.classList.toggle("active", on);
      btn.setAttribute("aria-selected", on ? "true" : "false");
    });
    Object.keys(els.panels).forEach(function (key) {
      els.panels[key].hidden = key !== tab;
    });
  }

  /** Coverage % → red (0) → yellow (50) → green (100). */
  function coverageColor(pct) {
    var p = Math.max(0, Math.min(100, Number(pct) || 0)) / 100;
    var a = p < 0.5
      ? { r: 224, g: 108, b: 117 }   // --red
      : { r: 214, g: 163, b: 74 };    // --yellow
    var b = p < 0.5
      ? { r: 214, g: 163, b: 74 }    // --yellow
      : { r: 78, g: 195, b: 138 };   // --green
    var t = p < 0.5 ? p * 2 : (p - 0.5) * 2;
    return "rgb(" +
      Math.round(a.r + (b.r - a.r) * t) + "," +
      Math.round(a.g + (b.g - a.g) * t) + "," +
      Math.round(a.b + (b.b - a.b) * t) + ")";
  }

  function mixSegments(s) {
    return [
      { key: "tested", label: "Tested", value: s.tested || 0, cls: "is-ok" },
      { key: "new", label: "Brand-new", value: s.brandNew || 0, cls: "is-new" },
      { key: "known", label: "Known gaps", value: s.knownUntested || 0, cls: "is-gap" },
      { key: "dep", label: "Deprecated", value: s.deprecated || 0, cls: "is-dep" },
    ];
  }

  function renderSummary(data) {
    if (!els.summary) return;
    var s = data.summary;
    var segs = mixSegments(s);
    var total = segs.reduce(function (n, seg) { return n + seg.value; }, 0) || 1;
    var bars = segs.filter(function (seg) { return seg.value > 0; }).map(function (seg) {
      var pct = Math.max(0.6, (seg.value / total) * 100);
      return (
        '<span class="cov-stack-seg ' + seg.cls + '" style="width:' + pct + '%" ' +
          'title="' + esc(seg.label) + ": " + esc(seg.value) + '"></span>'
      );
    }).join("");
    var legend = segs.map(function (seg) {
      return (
        '<span class="cov-stack-key">' +
          '<span class="cov-stack-dot ' + seg.cls + '"></span>' +
          '<strong>' + esc(seg.value) + "</strong> " + esc(seg.label) +
        "</span>"
      );
    }).join("");
    els.summary.innerHTML =
      '<div class="cov-bar-hero">' +
        '<div class="cov-bar-hero-top">' +
          '<div class="cov-bar-pct" style="color:' + coverageColor(s.coveragePercent) + '">' +
            esc(s.coveragePercent) + '<span>%</span></div>' +
          '<div class="cov-bar-copy">' +
            '<div class="cov-bar-title">' + esc(s.tested) + " of " + esc(s.nonDeprecated) +
              " active ops covered</div>" +
            '<div class="cov-bar-sub">' + esc(s.untested) + " gaps · " +
              esc(s.highRiskGaps) + " high-risk · " +
              esc(s.mutatingGaps) + " mutating</div>" +
          "</div>" +
        "</div>" +
        '<div class="cov-stack" role="img" aria-label="Operations mix">' + bars + "</div>" +
        '<div class="cov-stack-keys">' + legend + "</div>" +
      "</div>";
  }

  function filteredQueue() {
    var q = (els.queueSearch.value || "").trim().toLowerCase();
    var gap = els.queueGap.value;
    var risk = els.queueRisk.value;
    return (state.data.queue || []).filter(function (row) {
      if (gap && row.gap !== gap) return false;
      if (risk && row.riskBand !== risk) return false;
      if (!q) return true;
      return (row.m + " " + row.p + " " + (row.category || "") + " " +
        (row.operationId || "")).toLowerCase().indexOf(q) !== -1;
    });
  }

  function whyPill(gap) {
    if (gap === "new") return '<span class="cov-pill cov-pill-new">brand-new</span>';
    return '<span class="cov-pill cov-pill-gap">known</span>';
  }

  function riskCell(row) {
    return (
      '<span class="cov-risk cov-risk-' + esc(row.riskBand) + '" title="Heuristic score ' +
        esc(row.risk) + '">' +
        esc(row.riskBand) +
      "</span>"
    );
  }

  function renderQueue() {
    var rows = filteredQueue();
    els.queueCount.textContent = rows.length + " in queue";
    if (!rows.length) {
      els.queueBody.innerHTML =
        '<tr><td colspan="5" class="state-msg">No gaps match the current filters.</td></tr>';
      return;
    }
    els.queueBody.innerHTML = rows.map(function (row) {
      return (
        "<tr>" +
          '<td class="cov-col-risk">' + riskCell(row) + "</td>" +
          '<td class="cov-col-method"><span class="cov-method-badge">' + esc(row.m) + "</span></td>" +
          '<td class="cov-col-path"><code class="cov-path" title="' + esc(row.p) + '">' + esc(row.p) + "</code></td>" +
          '<td class="cov-col-why">' + whyPill(row.gap) + "</td>" +
          '<td class="cov-col-cat" title="' + esc(row.category) + '">' +
            '<span class="cov-cat-cell">' + esc(row.category) + "</span>" +
          "</td>" +
        "</tr>"
      );
    }).join("");
  }

  function matchesDomainEp(ep, q, statusFilter) {
    if (statusFilter === "gaps" || statusFilter === "untested") {
      if (ep.status !== "untested") return false;
    } else if (statusFilter === "tested" && ep.status !== "tested") return false;
    else if (statusFilter === "deprecated" && ep.status !== "deprecated") return false;
    if (!q) return true;
    return (ep.m + " " + ep.p).toLowerCase().indexOf(q) !== -1;
  }

  function filteredCategories() {
    var q = (els.domainSearch.value || "").trim().toLowerCase();
    var statusFilter = els.domainStatus.value;
    var catFilter = els.domainCategory.value;
    return (state.data.categories || []).map(function (cat) {
      if (catFilter && cat.name !== catFilter) return null;
      if (statusFilter === "gaps" && cat.untested === 0) return null;
      var endpoints = cat.endpoints.filter(function (ep) {
        return matchesDomainEp(ep, q, statusFilter);
      });
      if (!endpoints.length) return null;
      return { cat: cat, endpoints: endpoints };
    }).filter(Boolean);
  }

  function statusPill(ep) {
    if (ep.status === "tested") return '<span class="cov-pill cov-pill-ok">tested</span>';
    if (ep.status === "deprecated") return '<span class="cov-pill cov-pill-dep">deprecated</span>';
    if (ep.gap === "new") return '<span class="cov-pill cov-pill-new">brand-new</span>';
    return '<span class="cov-pill cov-pill-gap">untested</span>';
  }

  function renderDomain() {
    var rows = filteredCategories();
    var epCount = rows.reduce(function (n, r) { return n + r.endpoints.length; }, 0);
    els.domainCount.textContent =
      epCount + " endpoint" + (epCount === 1 ? "" : "s") +
      " · " + rows.length + " categor" + (rows.length === 1 ? "y" : "ies");

    if (!rows.length) {
      els.groups.innerHTML = '<div class="state-msg">No endpoints match the current filters.</div>';
      return;
    }

    els.groups.innerHTML = rows.map(function (row) {
      var cat = row.cat;
      var open = state.expanded.has(cat.name);
      return (
        '<section class="cov-group' + (open ? " open" : "") + '" data-cat="' + esc(cat.name) + '">' +
          '<button type="button" class="group-header cov-cat-header" aria-expanded="' + open + '">' +
            '<span class="chevron" aria-hidden="true">\u25B6</span>' +
            '<span class="group-name">' + esc(cat.name) + "</span>" +
            '<span class="cov-bar" aria-hidden="true">' +
              '<span class="cov-bar-fill" style="width:' + cat.coveragePercent + '%"></span>' +
            "</span>" +
            '<span class="group-meta">' +
              esc(cat.coveragePercent) + "% · " +
              esc(cat.untested) + " gap" +
              (cat.maxGapRisk ? " · risk " + esc(cat.maxGapRisk) : "") +
            "</span>" +
          "</button>" +
          (open
            ? '<div class="cov-ep-list">' +
                '<table class="cov-queue cov-domain-table">' +
                  "<thead><tr>" +
                    '<th class="cov-col-risk">Risk</th>' +
                    '<th class="cov-col-method">Method</th>' +
                    '<th class="cov-col-path">Path</th>' +
                    '<th class="cov-col-why">Status</th>' +
                  "</tr></thead>" +
                  "<tbody>" +
                  row.endpoints.map(function (ep) {
                    return (
                      '<tr class="cov-ep-row cov-ep-' + esc(ep.status) + '">' +
                        '<td class="cov-col-risk">' +
                          (ep.riskBand
                            ? '<span class="cov-risk cov-risk-' + esc(ep.riskBand) +
                              '" title="Heuristic score ' + esc(ep.risk) + '">' +
                              esc(ep.riskBand) + "</span>"
                            : '<span class="cov-risk-empty">—</span>') +
                        "</td>" +
                        '<td class="cov-col-method"><span class="cov-method-badge">' +
                          esc(ep.m) + "</span></td>" +
                        '<td class="cov-col-path"><code class="cov-path" title="' +
                          esc(ep.p) + '">' + esc(ep.p) + "</code></td>" +
                        '<td class="cov-col-why">' + statusPill(ep) + "</td>" +
                      "</tr>"
                    );
                  }).join("") +
                  "</tbody>" +
                "</table>" +
              "</div>"
            : "") +
        "</section>"
      );
    }).join("");
  }

  function renderQuality() {
    var dq = state.data.dataQuality || {};
    var inv = dq.inventory;
    var cards =
      qualityCard(
        "Overlay-only deprecated",
        dq.overlayOnlyDeprecated,
        "Marked deprecated in the hand overlay but not in OpenAPI. Review and clean up."
      ) +
      qualityCard(
        "OpenAPI deprecated",
        dq.openapiDeprecated,
        "Flagged deprecated in the live QA spec."
      ) +
      qualityCard(
        "Stale overlay entries",
        dq.staleOverlayEntries,
        "Still in endpoints-data.js but gone from OpenAPI."
      ) +
      qualityCard(
        "Untracked (brand-new)",
        dq.untrackedNew,
        "In OpenAPI, never added to the curated overlay."
      ) +
      qualityCard(
        "Hand-tracked untested",
        dq.handTrackedUntested,
        "Known gaps already recorded as t:false."
      );

    var invBlock = "";
    if (inv) {
      invBlock =
        '<div class="cov-quality-section">' +
          '<h3>Suite hygiene <span class="cov-quiet">(from inventory)</span></h3>' +
          '<div class="cov-quality-grid">' +
            qualityCard("Untagged features", inv.untagged,
              (inv.untaggedPercent != null ? inv.untaggedPercent + "% of " + inv.features : "")) +
            qualityCard("Ignored features", inv.ignored, "Still parsed, marked @Ignore") +
            qualityCard("Feature methods", inv.features, (inv.cases || "—") + " parameterized cases") +
          "</div>" +
          (inv.byType
            ? '<p class="cov-quiet cov-type-line">Types: ' +
                Object.keys(inv.byType).map(function (k) {
                  return esc(k) + " " + esc(inv.byType[k]);
                }).join(" · ") +
              "</p>"
            : "") +
        "</div>";
    }

    els.quality.innerHTML =
      '<div class="cov-quality-section">' +
        "<h3>Coverage data smells</h3>" +
        '<div class="cov-quality-grid">' + cards + "</div>" +
      "</div>" +
      invBlock;
  }

  function qualityCard(title, value, note) {
    return (
      '<article class="cov-q-card">' +
        '<div class="cov-q-num">' + esc(value == null ? "—" : value) + "</div>" +
        '<div class="cov-q-title">' + esc(title) + "</div>" +
        (note ? '<div class="cov-q-note">' + esc(note) + "</div>" : "") +
      "</article>"
    );
  }

  function fillCategories(data) {
    var names = (data.categories || []).map(function (c) { return c.name; })
      .sort(function (a, b) { return a.toLowerCase().localeCompare(b.toLowerCase()); });
    names.forEach(function (name) {
      var opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      els.domainCategory.appendChild(opt);
    });
  }

  function setCopyState(label, kind) {
    els.copyQueue.textContent = label;
    els.copyQueue.classList.remove("is-copied", "is-copy-failed");
    if (kind === "ok") els.copyQueue.classList.add("is-copied");
    if (kind === "fail") els.copyQueue.classList.add("is-copy-failed");
  }

  function copyBacklog() {
    var rows = filteredQueue();
    var text = rows.map(function (r) {
      return "- [ ] `" + r.m + " " + r.p + "` (" + r.gap + ", risk " + r.riskBand + ")";
    }).join("\n");
    if (!text) return;

    var gen = ++state.copyGen;
    if (state.copyTimer) {
      clearTimeout(state.copyTimer);
      state.copyTimer = null;
    }

    function ok() {
      if (gen !== state.copyGen) return;
      setCopyState("Copied ✓", "ok");
      state.copyTimer = setTimeout(function () {
        if (gen !== state.copyGen) return;
        setCopyState("Copy backlog", null);
        state.copyTimer = null;
      }, 1800);
    }

    function fail() {
      if (gen !== state.copyGen) return;
      setCopyState("Copy failed", "fail");
      state.copyTimer = setTimeout(function () {
        if (gen !== state.copyGen) return;
        setCopyState("Copy backlog", null);
        state.copyTimer = null;
      }, 1800);
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(ok).catch(fail);
      return;
    }

    // Fallback for older browsers / insecure contexts
    try {
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.left = "-9999px";
      document.body.appendChild(ta);
      ta.select();
      var worked = document.execCommand("copy");
      document.body.removeChild(ta);
      if (worked) ok();
      else fail();
    } catch (e) {
      fail();
    }
  }

  function expandAllVisible() {
    filteredCategories().forEach(function (row) {
      state.expanded.add(row.cat.name);
    });
    renderDomain();
  }

  function applyDeepLink() {
    var params = new URLSearchParams(window.location.search);
    var tab = params.get("tab");
    var risk = params.get("risk");
    var gap = params.get("gap");
    var status = params.get("status");
    var q = params.get("q");

    if (risk && els.queueRisk) {
      var riskOk = Array.from(els.queueRisk.options).some(function (o) {
        return o.value === risk;
      });
      if (riskOk) els.queueRisk.value = risk;
    }
    if (gap && els.queueGap) {
      var gapOk = Array.from(els.queueGap.options).some(function (o) {
        return o.value === gap;
      });
      if (gapOk) els.queueGap.value = gap;
    }
    if (q && els.queueSearch) els.queueSearch.value = q;
    if (status && els.domainStatus) {
      var statusOk = Array.from(els.domainStatus.options).some(function (o) {
        return o.value === status;
      });
      if (statusOk) els.domainStatus.value = status;
    }

    var allowedTabs = { queue: 1, domain: 1, quality: 1 };
    if (status && !tab) tab = "domain";
    if ((risk || gap || q) && !tab) tab = "queue";
    if (tab && allowedTabs[tab]) state._deepLinkTab = tab;
    else state._deepLinkTab = "queue";
  }

  function wire() {
    els.tabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        setTab(btn.getAttribute("data-tab"));
      });
    });
    els.queueSearch.addEventListener("input", renderQueue);
    els.queueGap.addEventListener("change", renderQueue);
    els.queueRisk.addEventListener("change", renderQueue);
    els.copyQueue.addEventListener("click", copyBacklog);
    els.domainSearch.addEventListener("input", renderDomain);
    els.domainStatus.addEventListener("change", renderDomain);
    els.domainCategory.addEventListener("change", renderDomain);
    els.expandAll.addEventListener("click", expandAllVisible);
    els.collapseAll.addEventListener("click", function () {
      state.expanded.clear();
      renderDomain();
    });
    els.groups.addEventListener("click", function (e) {
      var btn = e.target.closest(".cov-cat-header");
      if (!btn) return;
      var section = btn.closest(".cov-group");
      var name = section && section.getAttribute("data-cat");
      if (!name) return;
      if (state.expanded.has(name)) state.expanded.delete(name);
      else state.expanded.add(name);
      renderDomain();
    });
  }

  fetch("data/coverage.json", { cache: "no-cache" })
    .then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    })
    .then(function (data) {
      state.data = data;
      renderSummary(data);
      fillCategories(data);
      // Start collapsed so Expand all is meaningful; queue tab is the default view.
      state.expanded.clear();
      els.riskHint.textContent = (data.source && data.source.riskNote) || "";
      els.methodologyBody.innerHTML =
        esc(data.source && data.source.methodology) +
        ' <a href="data/coverage.json" target="_blank" rel="noopener">Raw JSON</a>';
      els.provenance.textContent =
        "Generated " + data.generatedAt +
        " · OpenAPI " + (data.source && data.source.openapiFileMtimeUtc) +
        " · overlay " + (data.source && data.source.overlay);
      wire();
      applyDeepLink();
      renderQueue();
      renderDomain();
      renderQuality();
      setTab(state._deepLinkTab || "queue");
      state._deepLinkTab = null;
    })
    .catch(function (err) {
      if (els.summary) {
        els.summary.innerHTML =
          '<p class="cov-summary-lead">Failed to load coverage: ' + esc(err.message) + "</p>";
      }
      els.queueBody.innerHTML =
        '<tr><td colspan="5" class="state-msg">' + esc(err.message) + "</td></tr>";
    });
})();
