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
    summaryLead: document.getElementById("summary-lead"),
    summaryMeta: document.getElementById("summary-meta"),
    pies: document.getElementById("pies"),
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

  function polar(cx, cy, r, angle) {
    var rad = ((angle - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  }

  function pieSlice(cx, cy, r, start, end) {
    if (end - start >= 359.99) {
      return (
        '<circle cx="' + cx + '" cy="' + cy + '" r="' + r +
        '" fill="currentColor"/>'
      );
    }
    var a = polar(cx, cy, r, end);
    var b = polar(cx, cy, r, start);
    var large = end - start > 180 ? 1 : 0;
    return (
      'M ' + cx + " " + cy +
      " L " + b.x + " " + b.y +
      " A " + r + " " + r + " 0 " + large + " 1 " + a.x + " " + a.y +
      " Z"
    );
  }

  function renderPies(data) {
    var s = data.summary;
    var segments = [
      { label: "Tested", value: s.tested, color: "#3d6b55", note: "Active ops with a regression path" },
      { label: "Untested · brand-new", value: s.brandNew, color: "#8a6a2e", note: "In OpenAPI, not in the curated overlay" },
      { label: "Untested · known", value: s.knownUntested, color: "#6e4545", note: "Tracked in overlay as t:false" },
      { label: "Deprecated", value: s.deprecated, color: "#3a3a3a", note: "Excluded from coverage %" },
    ];
    var total = segments.reduce(function (n, seg) { return n + seg.value; }, 0);
    if (!total) {
      els.pies.innerHTML = '<div class="cov-pie-empty">No data</div>';
      return;
    }

    var cx = 90;
    var cy = 90;
    var r = 78;
    var angle = 0;
    var paths = segments.filter(function (seg) { return seg.value > 0; }).map(function (seg, idx) {
      var sweep = (seg.value / total) * 360;
      var start = angle;
      var end = angle + sweep;
      angle = end;
      var pct = ((seg.value / total) * 100).toFixed(1);
      var d = pieSlice(cx, cy, r, start, end);
      var common =
        ' class="cov-slice" data-label="' + esc(seg.label) + '"' +
        ' data-value="' + esc(seg.value) + '"' +
        ' data-pct="' + pct + '"' +
        ' data-note="' + esc(seg.note) + '"' +
        ' fill="' + seg.color + '"';
      if (d.charAt(0) === "<") {
        return (
          '<circle class="cov-slice" cx="' + cx + '" cy="' + cy + '" r="' + r + '"' +
          ' data-label="' + esc(seg.label) + '"' +
          ' data-value="' + esc(seg.value) + '"' +
          ' data-pct="' + pct + '"' +
          ' data-note="' + esc(seg.note) + '"' +
          ' fill="' + seg.color + '"/>'
        );
      }
      return "<path d=\"" + d + "\"" + common + "></path>";
    }).join("");

    var keys = segments.map(function (seg) {
      return (
        '<span class="cov-pie-key" title="' + esc(seg.label) + ": " + esc(seg.value) + '">' +
          '<span class="cov-pie-swatch" style="background:' + seg.color + '"></span>' +
          esc(seg.value) +
        "</span>"
      );
    }).join("");

    els.pies.innerHTML =
      '<div class="cov-pie">' +
        '<div class="cov-pie-chart">' +
          '<svg class="cov-pie-svg" viewBox="0 0 180 180" role="img" aria-label="Operations mix">' +
            paths +
            '<circle class="cov-pie-hole" cx="90" cy="90" r="48"></circle>' +
          "</svg>" +
          '<div class="cov-pie-center">' +
            '<div class="cov-pie-center-num">' + esc(s.coveragePercent) + "%</div>" +
            '<div class="cov-pie-center-label">coverage</div>' +
          "</div>" +
          '<div class="cov-pie-tip" id="pie-tip" hidden></div>' +
        "</div>" +
        '<div class="cov-pie-keys" aria-hidden="true">' + keys + "</div>" +
      "</div>";

    wirePieHover();
  }

  function wirePieHover() {
    var chart = els.pies.querySelector(".cov-pie-chart");
    var tip = document.getElementById("pie-tip");
    if (!chart || !tip) return;

    function hide() {
      tip.hidden = true;
      chart.querySelectorAll(".cov-slice.is-hot").forEach(function (el) {
        el.classList.remove("is-hot");
      });
    }

    chart.querySelectorAll(".cov-slice").forEach(function (slice) {
      slice.addEventListener("mouseenter", function () {
        chart.querySelectorAll(".cov-slice.is-hot").forEach(function (el) {
          el.classList.remove("is-hot");
        });
        slice.classList.add("is-hot");
        tip.innerHTML =
          '<div class="cov-pie-tip-label">' + esc(slice.getAttribute("data-label")) + "</div>" +
          '<div class="cov-pie-tip-val">' +
            esc(slice.getAttribute("data-value")) +
            ' <span class="cov-pie-pct">(' + esc(slice.getAttribute("data-pct")) + "%)</span>" +
          "</div>" +
          '<div class="cov-pie-tip-note">' + esc(slice.getAttribute("data-note")) + "</div>";
        tip.hidden = false;
      });
      slice.addEventListener("mousemove", function (e) {
        var rect = chart.getBoundingClientRect();
        var x = e.clientX - rect.left + 14;
        var y = e.clientY - rect.top + 14;
        var tipW = tip.offsetWidth || 160;
        var tipH = tip.offsetHeight || 70;
        if (x + tipW > rect.width - 4) x = e.clientX - rect.left - tipW - 10;
        if (y + tipH > rect.height - 4) y = e.clientY - rect.top - tipH - 10;
        tip.style.left = Math.max(4, x) + "px";
        tip.style.top = Math.max(4, y) + "px";
      });
      slice.addEventListener("mouseleave", hide);
    });
  }

  function renderSummary(data) {
    var s = data.summary;
    els.summaryLead.textContent =
      s.tested + " of " + s.nonDeprecated +
      " active ops have at least one regression path (" + s.coveragePercent + "%).";
    els.summaryMeta.innerHTML =
      '<span><strong>' + esc(s.untested) + "</strong> gaps</span>" +
      '<span class="cov-dot" aria-hidden="true">·</span>' +
      '<span><strong>' + esc(s.brandNew) + "</strong> brand-new</span>" +
      '<span class="cov-dot" aria-hidden="true">·</span>' +
      '<span><strong>' + esc(s.knownUntested) + "</strong> known</span>" +
      '<span class="cov-dot" aria-hidden="true">·</span>' +
      '<span><strong>' + esc(s.highRiskGaps) + "</strong> high-risk</span>" +
      '<span class="cov-dot" aria-hidden="true">·</span>' +
      '<span><strong>' + esc(s.mutatingGaps) + "</strong> mutating</span>" +
      '<span class="cov-dot" aria-hidden="true">·</span>' +
      "<span>OpenAPI <code>" + esc(data.source.openapiInfo && data.source.openapiInfo.version) + "</code></span>";
    renderPies(data);
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
      els.summaryLead.textContent = "Failed to load coverage: " + err.message;
      els.queueBody.innerHTML =
        '<tr><td colspan="5" class="state-msg">' + esc(err.message) + "</td></tr>";
    });
})();
