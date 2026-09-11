import { cp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { execFileSync } from "node:child_process";

const site = resolve(import.meta.dirname, "..");
const root = resolve(site, "..");
const build = resolve(site, "build");
const staticDir = resolve(site, "static");
const openapi = resolve(staticDir, "openapi.json");
const basePath = process.env.DOCS_BASE_PATH ?? "/OpenDomain/";
const normalizedBasePath = basePath.endsWith("/") ? basePath : `${basePath}/`;

execFileSync("python3", [resolve(root, "scripts", "export_openapi.py")], {
  cwd: root,
  stdio: "inherit",
});

await rm(build, { force: true, recursive: true });
await mkdir(build, { recursive: true });
await cp(staticDir, build, { recursive: true });
for (const asset of ["site.css", "site.js"]) {
  const source = resolve(site, "src", asset);
  const target = resolve(build, asset);
  const contents = await readFile(source, "utf8");
  await writeFile(target, contents.replaceAll("__BASE_PATH__", normalizedBasePath), "utf8");
}

const template = await readFile(resolve(site, "src", "index.html"), "utf8");
await writeFile(
  resolve(build, "index.html"),
  template.replaceAll("__BASE_PATH__", normalizedBasePath),
  "utf8",
);

const schema = JSON.parse(await readFile(openapi, "utf8"));
if (!schema.openapi || !schema.info?.title || !Object.keys(schema.paths ?? {}).length) {
  throw new Error("Generated OpenAPI document is incomplete.");
}

console.log(`Built OpenDomain documentation for ${normalizedBasePath}`);
