import { promises as fs } from "fs";
import path from "path";

const rootDir = process.cwd();
const summaryDir = path.join(rootDir, "data", "summary");
const outputDir = path.join(rootDir, "data", "generated");

const parseArgs = () => {
  const args = process.argv.slice(2);
  let month = null;

  for (let i = 0; i < args.length; i += 1) {
    const arg = args[i];
    if (arg === "--month") {
      month = args[i + 1];
      i += 1;
      continue;
    }
    if (arg.startsWith("--month=")) {
      month = arg.split("=")[1];
    }
  }

  if (!month) {
    throw new Error("请使用 --month YYYY-MM 指定需要生成的月份。");
  }

  if (!/^\d{4}-\d{2}$/.test(month)) {
    throw new Error(`月份格式不正确：${month}，请使用 YYYY-MM。`);
  }

  return { month };
};

const readJson = async (filePath) => {
  const raw = await fs.readFile(filePath, "utf-8");
  return JSON.parse(raw);
};

const ensureDir = async (dir) => {
  await fs.mkdir(dir, { recursive: true });
};

const sortByDateDesc = (items) =>
  items.sort((a, b) => new Date(b.date) - new Date(a.date));

const countBy = (items, key) =>
  items.reduce((acc, item) => {
    const value = item[key] || "其他";
    acc.set(value, (acc.get(value) || 0) + 1);
    return acc;
  }, new Map());

const mapToSortedArray = (map) =>
  Array.from(map.entries())
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);

const build = async () => {
  const { month } = parseArgs();
  await ensureDir(outputDir);

  const entries = await fs.readdir(summaryDir);
  const summaries = [];

  for (const entry of entries) {
    if (!entry.endsWith(".json")) continue;
    const summary = await readJson(path.join(summaryDir, entry));
    const slug = summary.slug ?? path.basename(entry, ".json");
    if (summary.date?.startsWith(month)) {
      summaries.push({ ...summary, slug });
    }
  }

  const sorted = sortByDateDesc(summaries);
  const report = {
    month,
    total: sorted.length,
    byJournal: mapToSortedArray(countBy(sorted, "journal")),
    bySubject: mapToSortedArray(countBy(sorted, "subject")),
    items: sorted,
    generatedAt: new Date().toISOString()
  };

  const outputPath = path.join(outputDir, `report-${month}.json`);
  await fs.writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(`报告已生成：${outputPath}`);
};

build().catch((error) => {
  console.error(error);
  process.exit(1);
});
