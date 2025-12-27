const formatDate = (value) => {
  const date = new Date(value);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(date);
};

const createArticleLink = (item) => {
  const url = new URL("article.html", window.location.origin);
  url.searchParams.set("slug", item.slug);
  return url.pathname + url.search;
};

const renderStats = (report) => {
  const statsContainer = document.getElementById("report-stats");
  const stats = [
    { label: "报告月份", value: report.month },
    { label: "文章总数", value: report.total },
    { label: "期刊数量", value: report.byJournal.length },
    { label: "学科数量", value: report.bySubject.length }
  ];

  statsContainer.innerHTML = stats
    .map(
      (stat) => `
        <div class="stat-card">
          <p class="meta">${stat.label}</p>
          <h3>${stat.value}</h3>
        </div>
      `
    )
    .join("");
};

const renderChart = (containerId, items) => {
  const container = document.getElementById(containerId);
  if (!items.length) {
    container.innerHTML = `<p class="meta">暂无统计数据。</p>`;
    return;
  }

  const max = Math.max(...items.map((item) => item.count));
  container.innerHTML = items
    .map((item) => {
      const width = max === 0 ? 0 : Math.round((item.count / max) * 100);
      return `
        <div class="chart-row">
          <span class="chart-label">${item.name}</span>
          <div class="chart-bar">
            <div class="chart-fill" style="width: ${width}%"></div>
          </div>
          <span class="chart-value">${item.count}</span>
        </div>
      `;
    })
    .join("");
};

const renderListBySubject = (items) => {
  const grouped = items.reduce((acc, item) => {
    const key = item.subject || "未分类";
    acc.set(key, [...(acc.get(key) || []), item]);
    return acc;
  }, new Map());

  const ordered = Array.from(grouped.entries()).sort((a, b) =>
    a[0].localeCompare(b[0], "zh-CN")
  );

  const container = document.getElementById("report-list");
  container.innerHTML = ordered
    .map(
      ([subject, entries]) => `
        <div class="list-group">
          <h3>${subject}</h3>
          <ul>
            ${entries
              .map(
                (entry) => `
                  <li>
                    <a href="${createArticleLink(entry)}">${entry.title}</a>
                    <span class="meta"> · ${entry.journal} · ${formatDate(
                      entry.date
                    )}</span>
                  </li>
                `
              )
              .join("")}
          </ul>
        </div>
      `
    )
    .join("");
};

const renderBriefs = (briefs) => {
  const container = document.getElementById("report-briefs");
  if (!briefs.length) {
    container.innerHTML = `<p class="meta">暂无简要信息。</p>`;
    return;
  }

  container.innerHTML = briefs
    .map(
      (brief) => `
        <article class="brief-card">
          <pre class="brief-text">${brief.formatted}</pre>
          <a class="brief-link" href="${createArticleLink(brief)}">查看详情</a>
        </article>
      `
    )
    .join("");
};

const bindMonthPicker = (month) => {
  const input = document.getElementById("month-input");
  const button = document.getElementById("month-submit");
  if (!input || !button) return;

  input.value = month;

  const updateMonth = () => {
    const selected = input.value;
    if (!selected) return;
    const url = new URL(window.location.href);
    url.searchParams.set("month", selected);
    window.location.href = url.toString();
  };

  button.addEventListener("click", updateMonth);
  input.addEventListener("change", updateMonth);
};

const load = async () => {
  const params = new URLSearchParams(window.location.search);
  const month = params.get("month") || new Date().toISOString().slice(0, 7);
  bindMonthPicker(month);

  const response = await fetch(`data/generated/report-${month}.json`);
  if (!response.ok) {
    throw new Error(
      `无法加载 ${month} 的报告数据，请先生成 report-${month}.json。`
    );
  }
  const report = await response.json();

  document.getElementById("report-title").textContent = `${month} 月度报告`;
  document.getElementById(
    "report-subtitle"
  ).textContent = `共收录 ${report.total} 篇文章 · 生成时间 ${formatDate(
    report.generatedAt
  )}`;

  renderStats(report);
  renderChart("chart-journal", report.byJournal);
  renderChart("chart-subject", report.bySubject);
  renderListBySubject(report.items);
  renderBriefs(report.briefs || []);
  bindMonthPicker(month);
};

load().catch((error) => {
  const statsContainer = document.getElementById("report-stats");
  statsContainer.innerHTML = `<p class="meta">${error.message}</p>`;
});
