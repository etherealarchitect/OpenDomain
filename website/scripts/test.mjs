import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";

const root = resolve(import.meta.dirname, "..");
const build = resolve(root, "build");
const required = ["index.html", "site.css", "site.js", "openapi.json"];
for (const file of required) await access(resolve(build, file));
const html = await readFile(resolve(build, "index.html"), "utf8");
if (html.includes("__BASE_PATH__") || html.includes("cdn.") || html.includes("unpkg")) throw new Error("build contains unresolved or floating asset references");
const schema = JSON.parse(await readFile(resolve(build, "openapi.json"), "utf8"));
if (!schema.openapi || !schema.info?.title || Object.keys(schema.paths ?? {}).length === 0) throw new Error("OpenAPI contract is incomplete");
console.log(`Documentation contract passed (${Object.keys(schema.paths).length} paths).`);
