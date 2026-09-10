const SCREENS = [
  ["control_tower", "1. Control Tower"],
  ["application_context", "2. Application Context"],
  ["evidence_reconciliation", "3. Evidence Reconciliation"],
  ["context_graph", "4. Context Graph"],
  ["hybrid_retrieval", "5. Hybrid Retrieval"],
  ["policy_authority", "6. Policy & Authority"],
  ["human_decision", "7. Human Decision"],
  ["decision_trace", "8. Decision Trace"],
  ["outcome_feedback", "9. Outcome & Feedback"],
  ["credit_memo", "10. Credit Memo"],
  ["fairness_eval", "11. Fairness / Impact"],
  ["failure_simulation", "12. Failure Simulation"],
];

const state = {
  catalog: null,
  tower: null,
  dossier: null,
  screen: "control_tower",
};

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
  ));
}

function badge(text, kind) {
  return `<span class="badge ${kind || ""}">${esc(text)}</span>`;
}

async function api(path, options) {
  const res = await fetch(path, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || data.error || res.statusText);
  return data;
}

function actorQuery() {
  const scenario = state.catalog.golden_scenarios.find((row) => row.scenario_id === $("scenario").value);
  const applicationId = scenario ? scenario.application_id : "SME-L001";
  const params = new URLSearchParams({
    application_id: applicationId,
    actor_tenant: $("tenant").value,
    actor_role: $("role").value,
    purpose: $("purpose").value,
  });
  return { applicationId, params };
}

function renderNav() {
  $("nav").innerHTML = SCREENS.map(([id, label]) => (
    `<button type="button" data-screen="${id}" class="${state.screen === id ? "active" : ""}">${esc(label)}</button>`
  )).join("");
  $("nav").querySelectorAll("button").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.screen = btn.dataset.screen;
      renderNav();
      renderPanel();
    });
  });
}

function table(headers, rows) {
  if (!rows || !rows.length) return `<p class="muted">None.</p>`;
  return `<table><thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>`;
}

function kv(pairs) {
  return `<div class="kv">${pairs.map(([k, v]) => `<div class="muted">${esc(k)}</div><div>${v}</div>`).join("")}</div>`;
}

function renderExpected() {
  const dossier = state.dossier;
  const scenario = dossier && dossier.scenario;
  if (!scenario) {
    $("expected").innerHTML = `<strong>Expected control state</strong><p class="muted">Select a golden scenario.</p>`;
    return;
  }
  const denied = dossier.denied;
  $("expected").innerHTML = `
    <strong data-testid="scenario-id">${esc(scenario.scenario_id)}</strong>
    · ${esc(scenario.title)}
    <p>${esc(scenario.expected_behavior)}</p>
    <p>${denied ? badge("DENY " + denied, "danger") : badge("tenant retrieve ALLOW", "ok")}
       ${badge("AI final approve: none", "warn")}
       ${badge("policy " + (dossier.flags && dossier.flags.flags ? "3.2" : "3.2"), "")}</p>
  `;
}

function renderTower() {
  const rows = (state.tower.applications || []).map((app) => {
    const health = (app.source_health || []).map((h) => `${h.source}:${h.state}`).join(" · ");
    return `<div class="card ${app.visible ? "" : "denied"}" data-app="${esc(app.application_id)}" data-visible="${app.visible}">
      <div class="mono">${esc(app.application_id)} ${app.scenario_hint ? badge(app.scenario_hint) : ""}</div>
      <div>${esc(app.applicant_name || "REDACTED")}</div>
      <div class="muted">${esc(app.current_stage || "")} · ${esc(app.status || app.denied || "")}</div>
      <div class="muted">${esc(health || "no source health")}</div>
      <div>${app.engine_result ? badge(app.engine_result) : ""} ${app.exception_class ? badge(app.exception_class, "warn") : ""}</div>
    </div>`;
  }).join("");
  $("panel").innerHTML = `<h2>Underwriting Control Tower</h2>
    <p class="muted">Visible same-tenant applications: ${state.tower.visible_count}. Cross-tenant rows are redacted.</p>
    <div class="grid">${rows}</div>`;
}

function renderContext() {
  const screen = state.dossier.screens.application_context;
  if (!screen || !screen.enabled) { $("panel").innerHTML = deny("No application context."); return; }
  const parties = (screen.parties || []).map((p) => `<tr>
    <td class="mono">${esc(p.party_id)}</td><td>${esc(p.party_type)}</td><td>${esc(p.display_name)}</td>
    <td>${esc(p.role_on_application || p.is_primary_applicant)}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>Application Context</h2>
    ${kv([
      ["Applicant", esc(screen.application.applicant_name)],
      ["Type", esc(screen.application.applicant_type)],
      ["Facility", `${esc(screen.application.product)} · INR ${esc(screen.application.requested_limit)}`],
      ["Task", esc(screen.task)],
      ["Identity", badge(screen.identity_state, screen.identity_state === "AMBIGUOUS" ? "warn" : "ok")],
      ["Sole trader distinct", screen.sole_trader_distinct ? badge("YES", "ok") : badge("legal-entity path")],
      ["Restricted eval excluded", screen.restricted_eval_excluded_from_runtime ? badge("YES", "ok") : badge("check")],
    ])}
    <h3>Parties</h3>${table(["Party", "Kind", "Name", "Role"], parties)}`;
}

function renderEvidence() {
  const screen = state.dossier.screens.evidence_reconciliation;
  const facts = (screen.facts || []).map((f) => `<tr>
    <td class="mono">${esc(f.evidence_id)}</td><td>${esc(f.source_system)}</td>
    <td>${esc(f.semantic_type)}</td><td>${esc(f.value)}</td>
    <td>${badge(f.freshness_state, f.freshness_state === "stale" || f.freshness_state === "unavailable" ? "warn" : "ok")}</td>
    <td>${esc(f.conflict_state)}</td><td class="muted">${esc(f.provenance)}</td></tr>`).join("");
  const conflicts = (screen.conflicts || []).map((c) => `<tr>
    <td>${esc(c.left_semantic_type)}=${esc(c.left_value)}</td>
    <td>${esc(c.right_semantic_type)}=${esc(c.right_value)}</td>
    <td>${badge("not averaged", "warn")}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>Evidence Reconciliation</h2>
    <p>Bank, tax, bureau and documents remain separate. Conflicts are visible. Nothing is averaged.</p>
    ${table(["Evidence", "Source", "Semantic type", "Value", "Freshness", "Conflict", "Provenance"], facts)}
    <h3>Conflicts</h3>${table(["Left", "Right", "Handling"], conflicts)}`;
}

function renderGraph() {
  const screen = state.dossier.screens.context_graph;
  const nodes = screen.nodes || [];
  const kinds = [...new Set(nodes.map((n) => n.kind))];
  const pos = {};
  kinds.forEach((kind, i) => {
    nodes.filter((n) => n.kind === kind).forEach((n, j) => {
      pos[n.node_id] = { x: 40 + i * 170, y: 36 + j * 52 };
    });
  });
  const lines = (screen.edges || []).map((e) => {
    const a = pos[e.subject]; const b = pos[e.object];
    if (!a || !b) return "";
    return `<line x1="${a.x + 60}" y1="${a.y}" x2="${b.x}" y2="${b.y}" stroke="#4a8ab5" stroke-width="1" />`;
  }).join("");
  const circles = nodes.map((n) => {
    const p = pos[n.node_id];
    const stale = n.freshness_state === "stale" || n.presented_as_current === false;
    return `<g>
      <rect x="${p.x - 8}" y="${p.y - 14}" width="150" height="28" rx="4" fill="${stale ? "#3a2a12" : "#243044"}" stroke="#c9a227"/>
      <text x="${p.x}" y="${p.y + 4}" fill="#e7edf4" font-size="10">${esc(n.kind)} · ${esc(n.label).slice(0, 18)}</text>
    </g>`;
  }).join("");
  const width = Math.max(900, kinds.length * 180);
  const ys = Object.values(pos).map((p) => p.y);
  const height = Math.max(360, (ys.length ? Math.max.apply(null, ys) : 40) + 40);
  $("panel").innerHTML = `<h2>Context Graph Explorer</h2>
    <p class="muted">Snapshot ${esc(screen.snapshot_id)} · policy ${esc(screen.policy_version)} · kinds ${esc((screen.kinds || []).join(", "))}</p>
    <svg class="graph" viewBox="0 0 ${width} ${height}">${lines}${circles}</svg>
    <h3>Excluded</h3>
    ${table(["Ref", "Code", "Detail"], (screen.excluded || []).map((x) => `<tr><td class="mono">${esc(x.ref)}</td><td>${esc(x.reason_code)}</td><td>${esc(x.detail)}</td></tr>`).join(""))}`;
}

function renderRetrieval() {
  const screen = state.dossier.screens.hybrid_retrieval;
  if (screen.denied) {
    $("panel").innerHTML = `<h2>Hybrid Retrieval</h2><div class="deny" data-testid="retrieval-deny">DENY ${esc(screen.denied)}. Zero hops. Vector is not policy.</div>
      ${table(["Layer", "Effect", "Rule"], (screen.layers || []).map((l) => `<tr><td>${esc(l.layer)}</td><td>${badge(l.effect, l.effect === "DENY" ? "danger" : "ok")}</td><td>${esc(l.rule)}</td></tr>`).join(""))}`;
    return;
  }
  const hops = (screen.hops || []).map((h) => `<tr>
    <td>${badge(h.family_label || h.family)}</td><td class="mono">${esc(h.tool)}</td>
    <td>${esc(h.need)}</td><td>${esc((h.source_refs || []).join(", "))}</td>
    <td>${h.controlling ? badge("controlling", "warn") : badge(h.authority, "muted")}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>Hybrid Retrieval Evidence</h2>
    <p>Families labelled: ${(screen.families || []).map((f) => badge(f)).join(" ")} · vector is not policy: ${screen.vector_is_not_policy}</p>
    ${table(["Family", "Tool", "Need", "Evidence refs", "Authority"], hops)}`;
}

function renderPolicy() {
  const screen = state.dossier.screens.policy_authority;
  const ai = Object.entries(screen.ai_final_actions || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${badge(v.effect, v.effect === "DENY" ? "danger" : "ok")}</td><td>${esc(v.reason)}</td></tr>`).join("");
  const actor = Object.entries(screen.actor_actions || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${badge(v.effect, v.effect === "DENY" ? "danger" : "ok")}</td><td>${esc(v.reason)}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>Active Policy & Authority Gate</h2>
    ${kv([
      ["Active policy", badge(screen.active_version, "ok")],
      ["Status", esc(screen.active_status)],
      ["Superseded", `${esc(screen.superseded_version)} is reference only`],
      ["Engine", esc(screen.engine && screen.engine.result)],
      ["Triggered rules", esc(((screen.engine && screen.engine.triggered_rule_ids) || []).join(", ") || "none")],
      ["Required human role", badge(screen.required_human_role, "warn")],
      ["LOS assigned (not controlling)", esc(screen.los_assigned_role)],
      ["Policy PASS ≠ APPROVE", badge("true", "ok")],
    ])}
    <h3>AI_AGENT final actions</h3>${table(["Action", "Effect", "Reason"], ai)}
    <h3>Current actor</h3>${table(["Action", "Effect", "Reason"], actor)}`;
}

function renderDecision() {
  const screen = state.dossier.screens.human_decision;
  if (!screen.enabled) { $("panel").innerHTML = deny("Human Decision screen flagged off."); return; }
  const actions = Object.entries(screen.actions || {}).map(([k, v]) =>
    `<button type="button" data-outcome="${k}" class="${v.effect === "ALLOW" ? "ok" : "danger"}">${esc(k)} · ${esc(v.effect)}</button>`
  ).join("");
  $("panel").innerHTML = `<h2>Human Decision / Escalation</h2>
    <p>${badge("AI cannot approve", "danger")} Required role: ${badge(screen.required_human_role, "warn")} · actor ${esc(screen.actor_role)} · AI APPROVE=${esc(screen.ai_approve_effect)}</p>
    <p class="muted">Recommendation is advisory. Recording a decision calls check_access_and_authority.</p>
    <div class="actions">
      <button type="button" data-outcome="REFER">REFER</button>
      <button type="button" data-outcome="ESCALATE">ESCALATE</button>
      ${actions}
    </div>
    <pre data-testid="decision-result">${esc(JSON.stringify(screen.recorded || { status: "not recorded" }, null, 2))}</pre>`;
  $("panel").querySelectorAll("[data-outcome]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const { applicationId } = actorQuery();
      const result = await api("/api/decision", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          application_id: applicationId,
          actor_role: $("role").value,
          actor_tenant: $("tenant").value,
          outcome: btn.dataset.outcome,
        }),
      });
      await loadCase();
      state.screen = "human_decision";
      renderPanel();
      const pre = document.querySelector("[data-testid=decision-result]");
      if (pre) pre.textContent = JSON.stringify(result, null, 2);
    });
  });
}

function renderTrace() {
  const screen = state.dossier.screens.decision_trace;
  if (!screen.enabled) { $("panel").innerHTML = deny("Decision Trace flagged off."); return; }
  const t = screen.trace || {};
  $("panel").innerHTML = `<h2>Decision Trace / Audit</h2>
    <p>${badge("no hidden chain-of-thought", "ok")} required fields present: ${screen.required_fields_present}</p>
    ${kv([
      ["Trace", esc(t.trace_id)],
      ["Context", esc(t.context_snapshot && t.context_snapshot.context_id)],
      ["Policy version", esc(t.policy_version)],
      ["Authority required", esc(t.authority_required)],
      ["Human action", esc(JSON.stringify(t.human_action))],
      ["Rationale", esc(t.concise_rationale)],
      ["Model", esc(t.versions && t.versions.model)],
    ])}
    <h3>Source evidence</h3>
    ${table(["ID", "Source", "Freshness", "Type"], (t.source_evidence || []).map((e) => `<tr><td class="mono">${esc(e.evidence_id)}</td><td>${esc(e.source)}</td><td>${esc(e.freshness_state)}</td><td>${esc(e.semantic_type)}</td></tr>`).join(""))}
    <h3>Retrieval route</h3>
    <pre>${esc(JSON.stringify(t.retrieval_route, null, 2))}</pre>`;
}

function renderFeedback() {
  const screen = state.dossier.screens.outcome_feedback;
  $("panel").innerHTML = `<h2>Outcome & Feedback</h2>
    <p>Feedback enters GOVERNED_REVIEW. It does not auto-write policy, ontology, prompts, models or gold labels.</p>
    <p>Blocked destinations: ${(screen.blocked_destinations || []).map((d) => badge(d, "warn")).join(" ")}</p>
    <div class="actions">
      <button type="button" data-fb="AI_ACCEPTED">Queue AI_ACCEPTED</button>
      <button type="button" data-fb="AI_REJECTED">Queue AI_REJECTED</button>
      <button type="button" data-fb="HUMAN_DECISION">Capture HUMAN_DECISION</button>
      <button type="button" data-fb="PORTFOLIO_OUTCOME">Capture PORTFOLIO_OUTCOME</button>
      <button type="button" id="ungoverned" class="danger">Probe ungoverned POLICY_BUNDLE write</button>
    </div>
    <pre data-testid="feedback-result">${esc(JSON.stringify(screen.queued, null, 2))}</pre>`;
  $("panel").querySelectorAll("[data-fb]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const { applicationId } = actorQuery();
      const result = await api("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          application_id: applicationId,
          actor_role: $("role").value,
          actor_tenant: $("tenant").value,
          feedback_type: btn.dataset.fb,
        }),
      });
      await loadCase();
      state.screen = "outcome_feedback";
      renderPanel();
      const pre = document.querySelector("[data-testid=feedback-result]");
      if (pre) pre.textContent = JSON.stringify(result, null, 2);
    });
  });
  $("ungoverned").addEventListener("click", async () => {
    const { applicationId } = actorQuery();
    const result = await api("/api/feedback/ungoverned", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ application_id: applicationId, destination: "POLICY_BUNDLE" }),
    });
    document.querySelector("[data-testid=feedback-result]").textContent = JSON.stringify(result, null, 2);
  });
}

function renderMemo() {
  const screen = state.dossier.screens.credit_memo;
  if (!screen.enabled) {
    $("panel").innerHTML = `<h2>AI-Assisted Analysis / Credit Memo</h2>
      <div class="deny">${esc(screen.blocked)}: ${esc(screen.reason)}</div>
      <p>This memo is not a final credit decision. Manual underwriting remains available.</p>
      ${screen.manual_underwriting ? `<pre>${esc(JSON.stringify(screen.manual_underwriting, null, 2))}</pre>` : ""}`;
    return;
  }
  const stmts = (screen.statements || []).map((s) => `<tr>
    <td>${esc(s.section)}</td><td>${s.kind === "INFERENCE" ? badge("[INFERENCE]", "warn") : badge("FACT:" + (s.evidence_ids || []).join(","), "ok")}</td>
    <td>${esc(s.text)}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>AI-Assisted Analysis / Credit Memo</h2>
    <p>${badge("not a final decision", "warn")} trust=${esc(screen.trust_class)} model=${esc(screen.model)} provenance=${esc(screen.provenance_coverage)}</p>
    ${table(["Section", "Grounding", "Statement"], stmts)}
    <pre>${esc(screen.rendered_text)}</pre>`;
}

function renderFairness() {
  const screen = state.dossier.screens.fairness_eval;
  const rows = (screen.rows || []).slice(0, 40).map((r) => `<tr>
    <td class="mono">${esc(r.eval_case_id)}</td><td>${esc(r.approved_eval_group)}</td>
    <td>${esc(r.applicant_type)}</td><td>${esc(r.segment)}</td>
    <td>${esc(r.historical_outcome)}</td><td>${esc(r.use_restriction)}</td></tr>`).join("");
  $("panel").innerHTML = `<h2>Fairness / Impact Evaluation</h2>
    <p>${badge("separated from runtime", "ok")} runtime_access=${screen.runtime_access} · legal cutoff invented=${screen.legal_cutoff_invented}</p>
    <p class="muted">${esc(screen.reason || screen.note || "")}</p>
    ${table(["Eval case", "Group", "Applicant type", "Segment", "Historical outcome", "Restriction"], rows)}`;
}

function renderFailure() {
  const screen = state.dossier.screens.failure_simulation;
  $("panel").innerHTML = `<h2>Failure Simulation / Manual Fallback</h2>
    ${screen.denied ? `<div class="deny" data-testid="cross-tenant-deny">CROSS_TENANT deny. No foreign-tenant content.</div>` : ""}
    <p>Probes: ${Object.entries(screen.probes || {}).map(([k, v]) => badge(k + " " + v)).join(" ")}</p>
    <div class="actions">
      <button type="button" id="probe-threshold">Invented threshold (GS-14)</button>
      <button type="button" id="probe-inject">Injection follow (GS-09)</button>
      <button type="button" id="probe-policy">Superseded policy (GS-12)</button>
    </div>
    <h3>Degraded mode</h3>
    <pre data-testid="failure-result">${esc(JSON.stringify(screen.degraded || screen.inspection, null, 2))}</pre>
    <h3>Untrusted documents</h3>
    ${table(["Doc", "Injection", "Text"], (screen.untrusted_documents || []).map((d) => `<tr><td>${esc(d.source_id)}</td><td>${badge(d.injection_detected, d.injection_detected ? "warn" : "")}</td><td>${esc(d.text)}</td></tr>`).join(""))}
    <h3>Manual underwriting</h3>
    <pre>${esc(JSON.stringify(screen.manual_underwriting, null, 2))}</pre>`;
  $("probe-threshold").onclick = async () => {
    const result = await api("/api/probe/invented-threshold");
    document.querySelector("[data-testid=failure-result]").textContent = JSON.stringify(result, null, 2);
  };
  $("probe-inject").onclick = async () => {
    const result = await api("/api/probe/injection");
    document.querySelector("[data-testid=failure-result]").textContent = JSON.stringify(result, null, 2);
  };
  $("probe-policy").onclick = async () => {
    const result = await api("/api/probe/superseded-policy");
    document.querySelector("[data-testid=failure-result]").textContent = JSON.stringify(result, null, 2);
  };
}

function deny(text) {
  return `<div class="deny">${esc(text)}</div>`;
}

function renderPanel() {
  renderExpected();
  if (state.dossier && state.dossier.denied && state.screen !== "control_tower" && state.screen !== "failure_simulation" && state.screen !== "hybrid_retrieval" && state.screen !== "decision_trace") {
    $("panel").innerHTML = `<h2>${esc(state.screen)}</h2><div class="deny" data-testid="isolation-deny">DENY CROSS_TENANT. Zero other-tenant content.</div>`;
    return;
  }
  const renderers = {
    control_tower: renderTower,
    application_context: renderContext,
    evidence_reconciliation: renderEvidence,
    context_graph: renderGraph,
    hybrid_retrieval: renderRetrieval,
    policy_authority: renderPolicy,
    human_decision: renderDecision,
    decision_trace: renderTrace,
    outcome_feedback: renderFeedback,
    credit_memo: renderMemo,
    fairness_eval: renderFairness,
    failure_simulation: renderFailure,
  };
  renderers[state.screen]();
}

async function loadCase() {
  const { params } = actorQuery();
  state.tower = await api("/api/tower?" + params.toString());
  state.dossier = await api("/api/dossier?" + params.toString());
  renderNav();
  renderPanel();
}

async function boot() {
  state.catalog = await api("/api/catalog");
  $("scenario").innerHTML = state.catalog.golden_scenarios.map((row) =>
    `<option value="${esc(row.scenario_id)}">${esc(row.scenario_id)} · ${esc(row.application_id)} · ${esc(row.title)}</option>`
  ).join("");
  $("role").innerHTML = state.catalog.roles.map((role) => `<option>${esc(role)}</option>`).join("");
  $("role").value = "CREDIT_ANALYST";
  ["scenario", "tenant", "role", "purpose"].forEach((id) => $(id).addEventListener("change", loadCase));
  $("reload").addEventListener("click", loadCase);
  renderNav();
  await loadCase();
}

boot().catch((err) => {
  $("panel").innerHTML = deny(err.message);
});
