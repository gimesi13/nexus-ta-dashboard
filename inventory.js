(function () {
  "use strict";

  var state = {
    rows: [],
    expandedAreas: new Set(),
    expandedSpecs: new Set(),
    expandedCases: new Set(),
    selectedTags: new Set(),
    tagMatchMode: "any", // "any" | "all"
  };

  var els = {
    kpis: document.getElementById("kpis"),
    search: document.getElementById("search"),
    area: document.getElementById("filter-area"),
    type: document.getElementById("filter-type"),
    tagRoot: document.getElementById("filter-tag"),
    tagTrigger: document.getElementById("filter-tag-trigger"),
    tagLabel: document.getElementById("filter-tag-label"),
    tagPanel: document.getElementById("filter-tag-panel"),
    tagOptions: document.getElementById("filter-tag-options"),
    tagClear: document.getElementById("filter-tag-clear"),
    tagModeAny: document.getElementById("tag-mode-any"),
    tagModeAll: document.getElementById("tag-mode-all"),
    resultCount: document.getElementById("result-count"),
    groups: document.getElementById("groups"),
    provenance: document.getElementById("provenance"),
    expandAll: document.getElementById("expand-all"),
    collapseAll: document.getElementById("collapse-all"),
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function sumCases(rows) {
    return rows.reduce(function (n, r) { return n + (r.cases || 1); }, 0);
  }

  function fmtTests(n) {
    return n + " test" + (n === 1 ? "" : "s");
  }

  function fmtFeatureMethods(n) {
    return n + " feature method" + (n === 1 ? "" : "s");
  }

  function collapseAreaChildren(area) {
    var prefix = area + "::";
    Array.from(state.expandedSpecs).forEach(function (key) {
      if (key.indexOf(prefix) === 0) state.expandedSpecs.delete(key);
    });
    Array.from(state.expandedCases).forEach(function (key) {
      if (key.indexOf(prefix) === 0) state.expandedCases.delete(key);
    });
    closeTagPopovers();
  }

  function collapseSpecChildren(area, spec) {
    var prefix = area + "::" + spec + "::";
    Array.from(state.expandedCases).forEach(function (key) {
      if (key.indexOf(prefix) === 0) state.expandedCases.delete(key);
    });
    closeTagPopovers();
  }

  function unique(rows, key) {
    var set = {};
    rows.forEach(function (r) {
      if (Array.isArray(r[key])) r[key].forEach(function (v) { set[v] = true; });
      else if (r[key]) set[r[key]] = true;
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

  function selectedTagList() {
    return Array.from(state.selectedTags);
  }

  function updateTagLabel() {
    var tags = selectedTagList();
    if (!tags.length) {
      els.tagLabel.textContent = "All tags";
      els.tagTrigger.classList.remove("has-selection");
      return;
    }
    els.tagTrigger.classList.add("has-selection");
    if (tags.length === 1) {
      els.tagLabel.textContent = tags[0];
      return;
    }
    if (tags.length === 2) {
      els.tagLabel.textContent = tags[0] + ", " + tags[1];
      return;
    }
    els.tagLabel.textContent = tags.length + " tags";
  }

  function fillTagMulti(values) {
    els.tagOptions.innerHTML = values.map(function (v) {
      return '<label class="multi-select-option">' +
        '<input type="checkbox" value="' + esc(v) + '" />' +
        '<span>' + esc(v) + "</span></label>";
    }).join("");
    updateTagLabel();
  }

  function setTagPanelOpen(open) {
    els.tagPanel.hidden = !open;
    els.tagTrigger.setAttribute("aria-expanded", open ? "true" : "false");
    els.tagRoot.classList.toggle("open", open);
  }

  function renderKpis(data) {
    var items = [
      { num: data.cases, label: "Tests", sub: fmtFeatureMethods(data.features) },
      { num: data.specs, label: "Specs", sub: "\u00a0" },
      { num: data.areas, label: "Areas", sub: "\u00a0" },
    ];
    els.kpis.innerHTML = items.map(function (i) {
      return '<div class="kpi">' +
        '<div class="kpi-num">' + i.num + "</div>" +
        '<div class="kpi-label">' + i.label + "</div>" +
        '<div class="kpi-sub">' + i.sub + "</div>" +
        "</div>";
    }).join("");
  }

  function isFiltering() {
    return !!(els.search.value.trim() || els.area.value || els.type.value || state.selectedTags.size);
  }

  function filtered() {
    var q = els.search.value.trim().toLowerCase();
    var area = els.area.value, type = els.type.value;
    var tags = selectedTagList();
    return state.rows.filter(function (r) {
      if (area && r.area !== area) return false;
      if (type && r.type !== type) return false;
      if (tags.length) {
        var rowTags = r.tags || [];
        var hit = state.tagMatchMode === "all"
          ? tags.every(function (t) { return rowTags.indexOf(t) !== -1; })
          : tags.some(function (t) { return rowTags.indexOf(t) !== -1; });
        if (!hit) return false;
      }
      if (q) {
        var hay = (r.name + " " + r.spec + " " + (r.tags || []).join(" ")).toLowerCase();
        if (hay.indexOf(q) === -1) return false;
      }
      return true;
    });
  }

  function groupRows(rows) {
    var areas = {};
    rows.forEach(function (r) {
      var a = areas[r.area] || (areas[r.area] = { area: r.area, specs: {}, cases: 0, methods: 0 });
      var s = a.specs[r.spec] || (a.specs[r.spec] = { spec: r.spec, rows: [], cases: 0 });
      s.rows.push(r);
      s.cases += r.cases || 1;
      a.cases += r.cases || 1;
      a.methods += 1;
    });
    return Object.keys(areas).sort().map(function (an) {
      var a = areas[an];
      a.specList = Object.keys(a.specs).sort().map(function (sn) { return a.specs[sn]; });
      a.specCount = a.specList.length;
      return a;
    });
  }

  function typeBadge(t) {
    var cls = "type-badge type-" + esc(t).replace(/\s+/g, ".");
    return '<span class="' + cls + '">' + esc(t) + "</span>";
  }

  var COPY_ICON =
    '<svg class="tag-copy-icon" width="10" height="10" viewBox="0 0 16 16" aria-hidden="true">' +
    '<rect x="5" y="5" width="8" height="9" rx="1.4" fill="none" stroke="currentColor" stroke-width="1.3"/>' +
    '<path d="M3 10.2V3.6A1.6 1.6 0 0 1 4.6 2H9.8" fill="none" stroke="currentColor" stroke-width="1.3"/>' +
    "</svg>";
  var CHECK_ICON =
    '<svg class="tag-copy-check" width="10" height="10" viewBox="0 0 16 16" aria-hidden="true">' +
    '<path d="M3 8.4l3.3 3.3L13 4.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' +
    "</svg>";

  function tagPill(tag) {
    return '<span class="tag-label" data-tag="' + esc(tag) + '" title="Copy tag" tabindex="0" role="button">' +
      '<span class="tag-text">' + esc(tag) + "</span>" + COPY_ICON + CHECK_ICON +
      "</span>";
  }

  function tagLabels(tags) {
    if (!tags || !tags.length) return "";
    var first = tags[0];
    var rest = tags.length - 1;
    var html = tagPill(first);
    if (rest > 0) {
      html += '<button type="button" class="tag-more" aria-expanded="false" aria-label="Show ' +
        rest + " more tag" + (rest === 1 ? "" : "s") + '">+' + rest + "</button>" +
        '<span class="tag-popover" role="tooltip">' +
        tags.map(tagPill).join("") +
        "</span>";
    }
    return html;
  }

  function caseKey(r) {
    return r.area + "::" + r.spec + "::" + r.name;
  }

  function caseTitleHtml(r) {
    return '<span class="case-title">' +
      '<span class="case-name">' + esc(r.name) + "</span>" +
      (r.ignored ? '<span class="case-ignored" title="@Ignore in source">Ignored</span>' : "") +
      "</span>";
  }

  function caseEndHtml(r) {
    return '<div class="case-end">' +
      '<span class="case-tags">' + tagLabels(r.tags) + "</span>" +
      '<span class="case-type">' + typeBadge(r.type) + "</span>" +
      "</div>";
  }

  function renderSteps(r) {
    if (!r.steps || !r.steps.length) return "";
    var steps = r.steps.map(function (s) {
      return '<li class="step step-' + esc(s.phase) + '"><span class="step-phase">' +
        esc(s.phase) + "</span> " + esc(s.label) + "</li>";
    }).join("");
    var note = r.paramNote
      ? '<p class="param-note">' + esc(r.paramNote) + "</p>"
      : (r.cases > 1 ? '<p class="param-note">' + r.cases + " parameterized runs</p>" : "");
    var ignored = r.ignored ? '<p class="param-note ignored-note">@Ignore in source</p>' : "";
    return '<div class="case-steps"><ol class="step-list">' + steps + "</ol>" + note + ignored + "</div>";
  }

  function renderCase(r) {
    var expandable = r.steps && r.steps.length;
    var end = caseEndHtml(r);
    var ignoredCls = r.ignored ? " is-ignored" : "";
    var chevron = expandable
      ? '<span class="chevron case-chevron">\u25B6</span>'
      : '<span class="case-chevron case-chevron-placeholder" aria-hidden="true"></span>';
    var title = caseTitleHtml(r);
    if (!expandable) {
      return '<div class="case-row' + ignoredCls + '" title="' + esc(r.name) +
        (r.ignored ? " (@Ignore)" : "") + '">' +
        chevron + title + end +
        "</div>";
    }
    var key = caseKey(r);
    var open = state.expandedCases.has(key);
    return '<div class="case-group' + ignoredCls + (open ? " open" : "") +
      '" data-case="' + esc(key) + '">' +
      '<div class="case-row case-header" role="button" tabindex="0" title="' +
        esc(r.name) + (r.ignored ? " (@Ignore)" : "") + '">' +
        chevron + title + end +
      "</div>" +
      renderSteps(r) +
      "</div>";
  }

  function specMeta(s) {
    var bits = [fmtTests(s.cases)];
    if (s.rows.length !== s.cases) bits.push(fmtFeatureMethods(s.rows.length));
    return '<span class="meta-primary">' + bits.join(" \u00b7 ") + "</span>";
  }

  function renderSpec(area, s) {
    var key = area + "::" + s.spec;
    var open = state.expandedSpecs.has(key);
    return '<div class="spec-group' + (open ? " open" : "") + '" data-key="' + esc(key) + '">' +
      '<button class="group-header spec-header" type="button">' +
        '<span class="chevron">\u25B6</span>' +
        '<span class="group-name">' + esc(s.spec) + "</span>" +
        '<span class="group-meta">' + specMeta(s) + "</span>" +
      "</button>" +
      '<div class="spec-body">' + s.rows.map(renderCase).join("") + "</div>" +
      "</div>";
  }

  function areaMeta(a) {
    return '<span class="meta-primary">' +
      fmtTests(a.cases) + " \u00b7 " + a.specCount + " specs \u00b7 " +
      fmtFeatureMethods(a.methods) +
      "</span>";
  }

  function renderArea(a) {
    var open = state.expandedAreas.has(a.area);
    return '<div class="area-group' + (open ? " open" : "") + '" data-area="' + esc(a.area) + '">' +
      '<button class="group-header area-header" type="button">' +
        '<span class="chevron">\u25B6</span>' +
        '<span class="group-name">' + esc(a.area) + "</span>" +
        '<span class="group-meta">' + areaMeta(a) + "</span>" +
      "</button>" +
      '<div class="area-body">' + a.specList.map(function (s) { return renderSpec(a.area, s); }).join("") + "</div>" +
      "</div>";
  }

  function render() {
    var rows = filtered();
    var totalCases = sumCases(state.rows);
    var shownCases = sumCases(rows);
    els.resultCount.textContent = shownCases + " of " + totalCases + " tests";
    var groups = groupRows(rows);
    if (!groups.length) {
      els.groups.innerHTML = '<div class="state-msg">No test cases match the filters.</div>';
      return;
    }
    els.groups.innerHTML = groups.map(renderArea).join("");
  }

  function onFilterChange() {
    if (isFiltering()) {
      var groups = groupRows(filtered());
      state.expandedAreas = new Set();
      state.expandedSpecs = new Set();
      groups.forEach(function (a) {
        state.expandedAreas.add(a.area);
        a.specList.forEach(function (s) { state.expandedSpecs.add(a.area + "::" + s.spec); });
      });
    } else {
      state.expandedAreas = new Set();
      state.expandedSpecs = new Set();
    }
    state.expandedCases = new Set();
    render();
  }

  function expandAll() {
    var groups = groupRows(filtered());
    groups.forEach(function (a) {
      state.expandedAreas.add(a.area);
      a.specList.forEach(function (s) { state.expandedSpecs.add(a.area + "::" + s.spec); });
    });
    render();
  }

  function collapseAll() {
    state.expandedAreas = new Set();
    state.expandedSpecs = new Set();
    state.expandedCases = new Set();
    render();
  }

  function closeTagPopovers(except) {
    document.querySelectorAll(".case-tags.popover-open").forEach(function (el) {
      if (except && el === except) return;
      el.classList.remove("popover-open");
      var btn = el.querySelector(".tag-more");
      if (btn) btn.setAttribute("aria-expanded", "false");
      var host = el.closest(".case-row, .case-group");
      if (host) host.classList.remove("tag-popover-active");
    });
  }

  function copyText(text) {
    if (window.isSecureContext && navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        var ok = document.execCommand("copy");
        document.body.removeChild(ta);
        if (ok) resolve(); else reject(new Error("execCommand failed"));
      } catch (err) {
        reject(err);
      }
    });
  }

  function copyTag(tagEl) {
    var text = tagEl.getAttribute("data-tag") || "";
    if (!text) return;
    copyText(text).then(function () {
      tagEl.classList.add("copied");
      clearTimeout(tagEl._copyTimer);
      tagEl._copyTimer = setTimeout(function () { tagEl.classList.remove("copied"); }, 1000);
    });
  }

  function wireEvents() {
    [els.search, els.area, els.type].forEach(function (el) {
      el.addEventListener("input", onFilterChange);
      el.addEventListener("change", onFilterChange);
    });
    els.tagTrigger.addEventListener("click", function (e) {
      e.stopPropagation();
      setTagPanelOpen(els.tagPanel.hidden);
    });
    els.tagPanel.addEventListener("click", function (e) { e.stopPropagation(); });
    els.tagOptions.addEventListener("change", function (e) {
      var input = e.target.closest("input[type='checkbox']");
      if (!input) return;
      if (input.checked) state.selectedTags.add(input.value);
      else state.selectedTags.delete(input.value);
      updateTagLabel();
      onFilterChange();
    });
    els.tagClear.addEventListener("click", function () {
      state.selectedTags.clear();
      els.tagOptions.querySelectorAll("input[type='checkbox']").forEach(function (cb) {
        cb.checked = false;
      });
      updateTagLabel();
      onFilterChange();
    });
    function setTagMatchMode(mode) {
      state.tagMatchMode = mode === "all" ? "all" : "any";
      els.tagModeAny.classList.toggle("active", state.tagMatchMode === "any");
      els.tagModeAll.classList.toggle("active", state.tagMatchMode === "all");
      onFilterChange();
    }
    els.tagModeAny.addEventListener("click", function () { setTagMatchMode("any"); });
    els.tagModeAll.addEventListener("click", function () { setTagMatchMode("all"); });
    document.addEventListener("click", function () { setTagPanelOpen(false); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setTagPanelOpen(false);
    });
    els.expandAll.addEventListener("click", expandAll);
    els.collapseAll.addEventListener("click", collapseAll);

    els.groups.addEventListener("click", function (e) {
      var tagLabel = e.target.closest(".tag-label");
      if (tagLabel) {
        e.stopPropagation();
        copyTag(tagLabel);
        return;
      }
      if (e.target.closest(".tag-popover")) {
        e.stopPropagation();
        return;
      }
      var tagMore = e.target.closest(".tag-more");
      if (tagMore) {
        e.stopPropagation();
        var wrap = tagMore.closest(".case-tags");
        var open = wrap.classList.toggle("popover-open");
        tagMore.setAttribute("aria-expanded", open ? "true" : "false");
        var host = wrap.closest(".case-row, .case-group");
        if (host) host.classList.toggle("tag-popover-active", open);
        if (open) closeTagPopovers(wrap);
        return;
      }
      var caseHeader = e.target.closest(".case-header");
      if (caseHeader) {
        var cg = caseHeader.closest(".case-group");
        var ckey = cg.getAttribute("data-case");
        cg.classList.toggle("open");
        if (cg.classList.contains("open")) state.expandedCases.add(ckey);
        else state.expandedCases.delete(ckey);
        return;
      }
      var areaHeader = e.target.closest(".area-header");
      if (areaHeader) {
        var ag = areaHeader.parentElement;
        var key = ag.getAttribute("data-area");
        var opening = !ag.classList.contains("open");
        ag.classList.toggle("open");
        if (opening) {
          state.expandedAreas.add(key);
        } else {
          state.expandedAreas.delete(key);
          collapseAreaChildren(key);
          render();
        }
        return;
      }
      var specHeader = e.target.closest(".spec-header");
      if (specHeader) {
        var sg = specHeader.parentElement;
        var skey = sg.getAttribute("data-key");
        var openingSpec = !sg.classList.contains("open");
        sg.classList.toggle("open");
        if (openingSpec) {
          state.expandedSpecs.add(skey);
        } else {
          state.expandedSpecs.delete(skey);
          var parts = skey.split("::");
          collapseSpecChildren(parts[0], parts[1]);
          render();
        }
      }
    });

    document.addEventListener("click", function () { closeTagPopovers(); });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeTagPopovers();
      if (e.key !== "Enter" && e.key !== " ") return;
      var tagLabel = e.target.closest(".tag-label");
      if (tagLabel) {
        e.preventDefault();
        copyTag(tagLabel);
        return;
      }
      var caseHeader = e.target.closest(".case-header");
      if (caseHeader) {
        e.preventDefault();
        caseHeader.click();
      }
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
      fillTagMulti(unique(state.rows, "tags"));
      els.provenance.textContent =
        "Generated " + data.generatedAt + " from " + data.source +
        " \u2014 parsed directly from *TestSteps.groovy.";
      wireEvents();
      render();
    })
    .catch(function (err) {
      els.groups.innerHTML =
        '<div class="state-msg">Failed to load inventory: ' + esc(err.message) + "</div>";
    });
})();
