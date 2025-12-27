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

const renderLatest = (items) => {
  const container = document.getElementById("latest");
  container.innerHTML = items
    .slice(0, 6)
    .map(
      (item) => `
        <article class="card">
          <p class="meta">${item.journal} · ${formatDate(item.date)}</p>
          <h3>${item.title}</h3>
          <p>${item.summary}</p>
          <a class="button" href="${createArticleLink(item)}">阅读详情</a>
        </article>
      `
    )
    .join("");
};

const groupBy = (items, key) => {
  return items.reduce((groups, item) => {
    const value = item[key] || "其他";
    if (!groups[value]) groups[value] = [];
    groups[value].push(item);
    return groups;
  }, {});
};

const renderGroupedList = (groups, containerId) => {
  const container = document.getElementById(containerId);
  container.innerHTML = Object.entries(groups)
    .map(
      ([group, items]) => `
        <div class="list-group">
          <h3>${group}</h3>
          <ul>
            ${items
              .map(
                (item) => `
                  <li>
                    <a href="${createArticleLink(item)}">${item.title}</a>
                    <span class="meta"> · ${formatDate(item.date)}</span>
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

const load = async () => {
  const response = await fetch("data/generated/articles.json");
  if (!response.ok) {
    throw new Error("无法加载文章列表，请先生成 JSON 数据。");
  }
  const items = await response.json();
  renderLatest(items);
  renderGroupedList(groupBy(items, "journal"), "by-journal");
  renderGroupedList(groupBy(items, "subject"), "by-subject");
};

load().catch((error) => {
  const latest = document.getElementById("latest");
  latest.innerHTML = `<p class="meta">${error.message}</p>`;
});
