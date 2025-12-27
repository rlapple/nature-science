const getSlug = () => {
  const params = new URLSearchParams(window.location.search);
  return params.get("slug");
};

const formatDate = (value) => {
  const date = new Date(value);
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric"
  }).format(date);
};

const load = async () => {
  const slug = getSlug();
  if (!slug) {
    throw new Error("缺少文章标识，请从首页进入。");
  }

  const response = await fetch(`data/generated/articles/${slug}.json`);
  if (!response.ok) {
    throw new Error("无法加载文章内容，请确认 JSON 已生成。");
  }

  const data = await response.json();

  document.getElementById("title").textContent = data.title;
  document.getElementById("summary").textContent = data.summary;
  document.getElementById("meta").textContent = `${data.journal} · ${data.subject} · ${formatDate(
    data.date
  )}`;
  document.getElementById("pdf").href = data.pdf;

  const markdown = window.marked.parse(data.markdown);
  document.getElementById("content").innerHTML = markdown;
};

load().catch((error) => {
  document.getElementById("content").innerHTML = `<p class="meta">${error.message}</p>`;
});
