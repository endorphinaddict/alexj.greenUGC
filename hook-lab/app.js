(function () {
  "use strict";
  const H = window.HookLab;
  const $ = id => document.getElementById(id);
  const FAV_KEY = "hooklab.favs.v1";

  let hooks = [];
  let favs = load();
  let showingFavs = false;

  function load() { try { return JSON.parse(localStorage.getItem(FAV_KEY)) || []; } catch (e) { return []; } }
  function save() { try { localStorage.setItem(FAV_KEY, JSON.stringify(favs)); } catch (e) {} }
  function toast(msg) { const t = $("toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(toast.t); toast.t = setTimeout(() => t.classList.remove("show"), 1400); }
  function esc(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }
  function copy(text) {
    const done = () => toast("Copied");
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, fallback); else fallback();
    function fallback() { const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); done(); } catch (e) {} ta.remove(); }
  }

  /* ---------- form ---------- */
  const catSel = $("category");
  Object.entries(H.CATEGORIES).forEach(([k, c]) => catSel.add(new Option(c.label, k)));

  function renderChips(boxId, items, textareaId) {
    const box = $(boxId); box.innerHTML = "";
    items.forEach(text => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "chip"; b.textContent = text;
      b.onclick = () => {
        const ta = $(textareaId); const cur = H.lines(ta.value);
        const i = cur.indexOf(text);
        if (i >= 0) cur.splice(i, 1); else cur.push(text);
        ta.value = cur.join("\n"); sync(textareaId, box);
      };
      box.appendChild(b);
    });
    sync(textareaId, box);
    $(textareaId).oninput = () => sync(textareaId, box);
  }
  function sync(textareaId, box) {
    const cur = H.lines($(textareaId).value);
    box.querySelectorAll(".chip").forEach(c => c.classList.toggle("on", cur.includes(c.textContent)));
  }
  function loadCategory() {
    const c = H.CATEGORIES[catSel.value];
    ["audiences", "pains", "benefits"].forEach(id => $(id).value = "");
    renderChips("audience-chips", c.audiences, "audiences");
    renderChips("pain-chips", c.pains, "pains");
    renderChips("benefit-chips", c.benefits, "benefits");
  }
  catSel.onchange = loadCategory;

  const selTypes = new Set();
  Object.entries(H.HOOK_TYPES).forEach(([k, t]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = t.label;
    b.onclick = () => { selTypes.has(k) ? selTypes.delete(k) : selTypes.add(k); b.classList.toggle("on"); };
    $("type-chips").appendChild(b);
  });
  $("offerType").onchange = () => { $("offer-wrap").hidden = $("offerType").value !== "custom"; };

  function inputs() {
    return {
      product: $("product").value.trim(),
      category: catSel.value,
      audiences: H.lines($("audiences").value),
      pains: H.lines($("pains").value),
      benefits: H.lines($("benefits").value),
      types: [...selTypes],
      offerType: $("offerType").value,
      offer: $("offer").value
    };
  }

  /* ---------- rendering ---------- */
  function hookText(h) {
    return `${h.spoken}\nOn-screen: ${h.onscreen}\nVisual: ${h.visual} B-roll: ${h.broll}.`;
  }
  function scriptText(s) {
    return ["HOOK", "PROBLEM", "SOLUTION", "CTA"].map(k => {
      const p = s[k.toLowerCase()];
      return `${k}\nSay: ${p.say}\nShow: ${p.show}\nOn-screen: ${p.text}`;
    }).join("\n\n");
  }
  function isFav(h) { return favs.some(f => f.id === h.id); }

  function card(h) {
    const el = document.createElement("article"); el.className = "card"; el.dataset.id = h.id;
    el.innerHTML = `
      <div class="meta"><span class="tag">${esc(h.typeLabel)}</span><span class="tag emo">${esc(h.emotion)}</span></div>
      <p class="say">${esc(h.spoken)}</p>
      <p class="row"><b>On-screen:</b> <span class="onscreen">${esc(h.onscreen)}</span></p>
      <p class="row"><b>Visual:</b> ${esc(h.visual)}</p>
      <p class="row"><b>B-roll:</b> ${esc(h.broll)}</p>
      <div class="actions">
        <button class="copy">Copy hook</button>
        <button class="reroll">Reroll</button>
        <button class="script-btn">Full script</button>
        <button class="fav ${isFav(h) ? "on" : ""}">${isFav(h) ? "★ Saved" : "☆ Save"}</button>
      </div>
      <div class="script" hidden></div>`;
    const scriptBox = el.querySelector(".script");
    el.querySelector(".copy").onclick = () => copy(hookText(h));
    el.querySelector(".reroll").onclick = () => {
      const n = H.reroll(h, inputs());
      const i = hooks.findIndex(x => x.id === h.id);
      if (i >= 0) hooks[i] = n; else { const j = favs.findIndex(x => x.id === h.id); if (j >= 0) favs[j] = n; save(); }
      render();
    };
    el.querySelector(".fav").onclick = () => {
      if (isFav(h)) favs = favs.filter(f => f.id !== h.id); else favs.push(Object.assign({}, h, { saved: Date.now() }));
      save(); render();
    };
    el.querySelector(".script-btn").onclick = () => {
      if (!scriptBox.hidden) { scriptBox.hidden = true; return; }
      const s = H.buildScript(h, inputs());
      scriptBox.innerHTML = ["hook", "problem", "solution", "cta"].map(k =>
        `<div class="step"><h4>${k}</h4><div><p>${esc(s[k].say)}</p><p class="row"><b>Show:</b> ${esc(s[k].show)}</p><p class="row"><b>On-screen:</b> <span class="onscreen">${esc(s[k].text)}</span></p></div></div>`
      ).join("") + `<div class="actions"><button class="copy-script">Copy script</button><button class="regen">Rewrite problem/solution/CTA</button></div>`;
      scriptBox.hidden = false;
      scriptBox.querySelector(".copy-script").onclick = () => copy(scriptText(s));
      scriptBox.querySelector(".regen").onclick = () => { scriptBox.hidden = true; el.querySelector(".script-btn").click(); };
    };
    return el;
  }

  function render() {
    const list = showingFavs ? favs : hooks;
    const out = $("out"); out.innerHTML = "";
    $("count").textContent = list.length ? `(${list.length}${showingFavs ? " saved" : ""})` : "";
    $("show-favs").textContent = showingFavs ? "← Back to results" : `★ Saved (${favs.length})`;
    if (!list.length) {
      out.innerHTML = `<div class="empty">${showingFavs ? "Nothing saved yet. Tap ☆ Save on any hook." : "Fill in the product on the left and hit <b>Generate hooks</b>."}</div>`;
      return;
    }
    list.forEach(h => out.appendChild(card(h)));
  }

  $("generate").onclick = () => {
    showingFavs = false;
    hooks = H.generate(inputs(), parseInt($("perType").value, 10));
    render();
    $("out").scrollIntoView({ behavior: "smooth", block: "start" });
  };
  $("show-favs").onclick = () => { showingFavs = !showingFavs; render(); };
  $("copy-favs").onclick = () => {
    if (!favs.length) return toast("Nothing saved yet");
    copy(favs.map((h, i) => `${i + 1}. [${h.typeLabel}] ${hookText(h)}`).join("\n\n"));
  };

  loadCategory();
  render();
})();
