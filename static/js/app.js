// EstateIQ AI: UI logic. Prices come from /api/predict; the chat below is still a demo until Step 4.
const $ = (s, r = document) => r.querySelector(s);

let DATA = null, LISTINGS = [], active = "All";

// Pakistani number format: lakh / crore
function pkr(n) {
  if (n >= 1e7) return "PKR " + (n / 1e7).toFixed(2) + " crore";
  if (n >= 1e5) return "PKR " + (n / 1e5).toFixed(1) + " lakh";
  return "PKR " + Math.round(n).toLocaleString("en-PK");
}

// Count-up numbers
function count(el, to, fmt = v => Math.round(v).toLocaleString()) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return (el.textContent = fmt(to));
  const t0 = performance.now();
  (function tick(t) {
    const p = Math.min((t - t0) / 1000, 1);
    el.textContent = fmt(to * (1 - Math.pow(1 - p, 3)));
    if (p < 1) requestAnimationFrame(tick);
  })(t0);
}

// Estimator: calls the trained model through the API
const form = $("#est"), priceEl = $("#price");
let timer, seq = 0;
async function estimate() {
  const f = new FormData(form), id = ++seq;
  $("#bed-out").textContent = f.get("bedrooms");
  $("#bath-out").textContent = f.get("baths");
  if (!(+f.get("area") > 0)) { priceEl.textContent = "—"; $("#range").textContent = "Enter a size to see a range"; return; }
  priceEl.classList.add("swap");
  try {
    const r = await fetch("/api/predict", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city: f.get("city"), location: f.get("location"), area: +f.get("area"),
        unit: f.get("unit"), bedrooms: +f.get("bedrooms"), baths: +f.get("baths") }),
    });
    const d = await r.json();
    if (id !== seq) return;
    if (!r.ok) throw new Error(d.detail || "The estimate failed.");
    priceEl.textContent = pkr(d.price);
    $("#range").textContent = `Likely range ${pkr(d.low)} to ${pkr(d.high)}`;
  } catch (e) {
    if (id !== seq) return;
    priceEl.textContent = "—"; $("#range").textContent = e.message;
  }
  priceEl.classList.remove("swap");
}
form.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(estimate, 250); });
form.addEventListener("submit", e => e.preventDefault());

function fillLocations() {
  const city = $("#city").value;
  $("#loc").innerHTML = DATA.cities[city].map(l => `<option>${l}</option>`).join("") || "<option value=''>Any area</option>";
}
$("#city").addEventListener("change", fillLocations);

function drawCards() {
  const rows = LISTINGS.filter(l => active === "All" || l.city === active);
  $("#cards").innerHTML = rows.length ? rows.map(l => `
    <article class="card"><div class="pic">House in ${l.location}</div>
      <div class="in"><h3>${pkr(l.price)}</h3><p>${l.location}, ${l.city}</p>
      <ul><li>${l.bedrooms} beds</li><li>${l.baths} baths</li><li>${Math.round(l.area_sqft).toLocaleString()} sq ft</li></ul></div></article>`).join("")
    : `<div class="empty">No properties in this city in the featured set. Try another city.</div>`;
}

async function init() {
  try {
    DATA = await (await fetch("/api/options")).json();
  } catch {
    $("#range").textContent = "Could not load data. Is the server running?"; return;
  }
  const cities = Object.keys(DATA.ppsf);
  $("#city").innerHTML = cities.map(c => `<option>${c}</option>`).join("");
  fillLocations();
  count($("#s-props"), DATA.stats.listings);
  count($("#s-cities"), cities.length);
  count($("#s-avg"), DATA.stats.median_price, pkr);
  estimate();

  const max = Math.max(...Object.values(DATA.ppsf));
  $("#bars").innerHTML = Object.entries(DATA.ppsf).map(([c, r]) =>
    `<div class="bar"><span>${c}</span><div class="track"><div class="fill" data-w="${(r / max) * 100}"></div></div><span>${Math.round(r).toLocaleString()}</span></div>`).join("");
  new IntersectionObserver((es, ob) => es.forEach(e => {
    if (e.isIntersecting) { e.target.querySelectorAll(".fill").forEach(f => (f.style.width = f.dataset.w + "%")); ob.unobserve(e.target); }
  }), { threshold: 0.3 }).observe($("#bars"));

  LISTINGS = DATA.featured;
  const tabs = ["All", ...new Set(LISTINGS.map(l => l.city))];
  $("#chips").innerHTML = tabs.map(c => `<button type="button" class="chip" aria-pressed="${c === active}">${c}</button>`).join("");
  drawCards();
}
$("#chips").addEventListener("click", e => {
  const b = e.target.closest(".chip"); if (!b) return;
  active = b.textContent;
  document.querySelectorAll("#chips .chip").forEach(x => x.setAttribute("aria-pressed", x === b));
  drawCards();
});
init();

// Assistant (canned replies; replace say() with a fetch to your FastAPI chat endpoint in Step 5)
const log = $("#log");
const ANSWERS = {
  budget: "PKR 2 crore is just under the median house price in Karachi and Lahore in this data. Try the estimator with your size and area to see what fits.",
  cheapest: "By median asking rate per square foot, Lahore is the lowest of the cities in the data and Karachi the highest. See the Market section.",
  marla: "One marla is about 272 square feet, and one kanal is 20 marla. The estimator converts these for you.",
};
const SUGGEST = [["What can I buy for 2 crore?", "budget"], ["Which city is cheapest?", "cheapest"], ["How big is a marla?", "marla"]];
$("#suggest").innerHTML = SUGGEST.map(([t, k]) => `<button type="button" class="chip" data-k="${k}">${t}</button>`).join("");
function add(text, who) {
  const d = document.createElement("div");
  d.className = "msg " + who; d.textContent = text; log.append(d); log.scrollTop = log.scrollHeight;
}
function say(q, key) {
  add(q, "you");
  setTimeout(() => add(ANSWERS[key] || "I can't answer that yet. Live answers arrive with the AI assistant step.", "bot"), 450);
}
$("#suggest").addEventListener("click", e => { const b = e.target.closest(".chip"); if (b) say(b.textContent, b.dataset.k); });
$("#ask").addEventListener("submit", e => {
  e.preventDefault();
  const q = $("#q").value.trim(); if (!q) return;
  const s = q.toLowerCase();
  say(q, s.includes("marla") ? "marla" : s.includes("cheap") ? "cheapest" : s.includes("budget") || s.includes("crore") ? "budget" : "");
  $("#q").value = "";
});

// Highlight current section in nav
const links = [...document.querySelectorAll("#nav a")];
const io = new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) links.forEach(a => a.classList.toggle("on", a.getAttribute("href") === "#" + e.target.id));
}), { rootMargin: "-40% 0px -55% 0px" });
document.querySelectorAll("main section").forEach(s => io.observe(s));
