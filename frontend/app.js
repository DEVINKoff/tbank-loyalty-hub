const API_URL = new URLSearchParams(location.search).get("api") || "http://localhost:8000";

const app = document.querySelector("#app");
const userSelect = document.querySelector("#userSelect");
const themeToggle = document.querySelector("#themeToggle");

const currencyLabels = {
  rub: "₽",
  miles: "миль",
  "bravo-points": "Браво",
};

themeToggle.addEventListener("click", () => {
  document.documentElement.classList.toggle("dark");
  themeToggle.textContent = document.documentElement.classList.contains("dark") ? "☀️" : "🌙";
});

async function fetchJson(path, fallbackPath) {
  try {
    const response = await fetch(`${API_URL}${path}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    if (!fallbackPath) throw error;
    const fallback = await fetch(fallbackPath);
    return await fallback.json();
  }
}

function formatValue(value, currency) {
  return `${Number(value || 0).toLocaleString("ru-RU")} ${currencyLabels[currency] || currency}`;
}

function chartValue(row) {
  return Object.entries(row)
    .filter(([key]) => key !== "month")
    .reduce((sum, [, value]) => sum + Number(value || 0), 0);
}

function renderUsers(users) {
  userSelect.innerHTML = users
    .map((user) => `<option value="${user.id}">${user.full_name} · ${user.financial_segment}</option>`)
    .join("");

  userSelect.addEventListener("change", () => loadSummary(userSelect.value));
}

function renderSummary(data) {
  const totals = Object.entries(data.totals_by_currency);
  const forecast = Object.entries(data.forecast);
  const maxChart = Math.max(1, ...data.monthly_chart.map(chartValue));
  const lastMonths = data.monthly_chart.slice(-8);

  app.innerHTML = `
    <section class="hero-grid">
      <article class="card main-card">
        <div>
          <span class="segment">${data.user.segment_label || data.user.financial_segment}</span>
          <h2>${data.user.full_name}</h2>
          <p class="muted">Вся выгода клиента в одном месте: программы, партнёры, прогноз и механики удержания.</p>
          <div class="total-row">
            ${totals.map(([currency, value]) => `
              <div class="metric">
                <strong>${Number(value).toLocaleString("ru-RU")}</strong>
                <span>${currencyLabels[currency] || currency}</span>
              </div>
            `).join("")}
          </div>
        </div>
        <p class="muted">Транзакций лояльности: ${data.transaction_count}. Счетов: ${data.accounts.length}.</p>
      </article>

      <article class="card">
        <div class="section-title">
          <h2>Прогноз</h2>
          <span class="muted">на основе 3 месяцев</span>
        </div>
        <div class="list">
          ${forecast.map(([currency, item]) => `
            <div class="list-item">
              <strong>${formatValue(item.next_month, currency)} / месяц</strong>
              <p class="muted">${formatValue(item.next_year, currency)} за год при текущем поведении.</p>
            </div>
          `).join("")}
        </div>
      </article>
    </section>

    <section class="grid-2">
      <article class="card">
        <div class="section-title">
          <h2>Динамика выгоды</h2>
          <span class="muted">последние месяцы</span>
        </div>
        <div class="chart">
          ${lastMonths.map((row) => {
            const total = chartValue(row);
            const width = Math.max(4, Math.round(total / maxChart * 100));
            return `
              <div class="bar-row">
                <span>${row.month}</span>
                <div class="bar-track"><div class="bar" style="--width:${width}%"></div></div>
                <strong>${total}</strong>
              </div>
            `;
          }).join("")}
        </div>
      </article>

      <article class="card">
        <div class="section-title">
          <h2>ИИ-подсказки</h2>
          <span class="muted">объяснимо</span>
        </div>
        <div class="list">
          ${data.ai_insights.map((text) => `<div class="list-item">${text}</div>`).join("")}
        </div>
      </article>
    </section>

    <section class="card">
      <div class="section-title">
        <h2>Лучшие партнёрские акции</h2>
        <span class="muted">под сегмент ${data.user.financial_segment}</span>
      </div>
      <div class="grid-3">
        ${data.offers.map((offer) => `
          <article class="card offer" style="--offer-color:${offer.brand_color_hex}">
            <span class="badge">${offer.cashback_percent}%</span>
            <h3>${offer.partner_name}</h3>
            <p class="muted">${offer.short_description}</p>
            <a class="cta" href="#">Активировать</a>
          </article>
        `).join("")}
      </div>
    </section>

    <section class="grid-2">
      <article class="card">
        <div class="section-title">
          <h2>Миссии</h2>
          <span class="muted">геймификация</span>
        </div>
        <div class="list">
          ${data.missions.map((mission) => `
            <div class="list-item mission">
              <strong>${mission.title}</strong>
              <span class="muted">${mission.description}</span>
              <div class="progress"><div style="--progress:${mission.progress}%"></div></div>
            </div>
          `).join("")}
        </div>
      </article>

      <article class="card">
        <div class="section-title">
          <h2>Экосистема</h2>
          <span class="muted">умный cross-sell</span>
        </div>
        <div class="list">
          ${data.cross_sell.map((item) => `
            <div class="list-item">
              <strong>${item.product}</strong>
              <p class="muted">${item.reason}</p>
              <a class="cta" href="#">${item.cta}</a>
            </div>
          `).join("")}
        </div>
      </article>
    </section>
  `;
}

async function loadSummary(userId = "1") {
  app.innerHTML = `<section class="skeleton">Загрузка профиля...</section>`;
  const data = await fetchJson(`/api/users/${userId}/loyalty-summary`, "./public/sample-response.json");
  renderSummary(data);
}

async function init() {
  try {
    const users = await fetchJson("/api/users", "./public/users.json");
    renderUsers(users);
    await loadSummary(users[0]?.id || "1");
  } catch (error) {
    const template = document.querySelector("#errorTemplate");
    app.innerHTML = template.innerHTML;
  }
}

init();
