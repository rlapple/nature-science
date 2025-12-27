import { promises as fs } from "fs";
import path from "path";

const rootDir = process.cwd();
const summaryDir = path.join(rootDir, "data", "summary");
const markdownDir = path.join(rootDir, "data", "md");
const outputDir = path.join(rootDir, "data", "generated");
const detailDir = path.join(outputDir, "articles");

const ensureDir = async (dir) => {
  await fs.mkdir(dir, { recursive: true });
};

const readJson = async (filePath) => {
  const raw = await fs.readFile(filePath, "utf-8");
  return JSON.parse(raw);
};

const readMarkdown = async (slug, mdFile) => {
  const fileName = mdFile ?? `${slug}.md`;
  const mdPath = path.join(markdownDir, fileName);
  return fs.readFile(mdPath, "utf-8");
};

const loadSummaries = async () => {
  const entries = await fs.readdir(summaryDir);
  const summaries = [];

  for (const entry of entries) {
    if (!entry.endsWith(".json")) continue;
    const filePath = path.join(summaryDir, entry);
    const summary = await readJson(filePath);
    const slug = summary.slug ?? path.basename(entry, ".json");
    summaries.push({ ...summary, slug });
  }

  return summaries;
};

const build = async () => {
  await ensureDir(detailDir);

  const summaries = await loadSummaries();
  const detailItems = [];

  for (const summary of summaries) {
    const markdown = await readMarkdown(summary.slug, summary.mdFile);
    const detail = {
      ...summary,
      markdown,
      updatedAt: new Date().toISOString()
    };
    const detailPath = path.join(detailDir, `${summary.slug}.json`);
    await fs.writeFile(detailPath, `${JSON.stringify(detail, null, 2)}\n`);

    detailItems.push({
      ...summary,
      detailPath: `data/generated/articles/${summary.slug}.json`
    });
  }

  detailItems.sort((a, b) => new Date(b.date) - new Date(a.date));

  const listPath = path.join(outputDir, "articles.json");
  await fs.writeFile(listPath, `${JSON.stringify(detailItems, null, 2)}\n`);
};

build().catch((error) => {
  console.error(error);
  process.exit(1);
});
