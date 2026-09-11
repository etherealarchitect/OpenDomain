import { spawnSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync, readFileSync, writeFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const rootDir = join(__dirname, '../..');
const websiteDir = join(__dirname, '..');

console.log('🔄 Building OpenDomain documentation website...');

// Check if Docusaurus is installed
try {
  const result = spawnSync('npx', ['@docusaurus/core', '--version'], {
    cwd: websiteDir,
    stdio: 'pipe',
    encoding: 'utf-8',
  });

  if (result.status !== 0) {
    console.log('📦 Installing Docusaurus and dependencies...');

    // Create package.json if it doesn't exist with proper config
    const packageJsonContent = {
      name: "opendomain-docs",
      version: "0.1.0",
      private: true,
      scripts: {
        "start": "docusaurus start",
        "build": "docusaurus build",
        "swizzle": "docusaurus swizzle",
        "deploy": "docusaurus deploy",
        "clear": "docusaurus clear",
        "serve": "docusaurus serve",
        "write-translations": "docusaurus write-translations",
        "write-heading-ids": "docusaurus write-heading-ids"
      },
      dependencies: {
        "@docusaurus/core": "^3.5.0",
        "@docusaurus/plugin-content-docs": "^3.5.0",
        "@docusaurus/preset-classic": "^3.5.0",
        "@docusaurus/theme-classic": "^3.5.0",
        "@docusaurus-preset-openapi": "^0.9.0",
        "clsx": "^2.0.0",
        "prism-react-renderer": "^2.3.0",
        "react": "^18.2.0",
        "react-dom": "^18.2.0"
      },
      browserslist: {
        production: [
          ">0.5%",
          "not dead",
          "not op_mini all"
        ],
        development: [
          "last 1 chrome version",
          "last 1 firefox version",
          "last 1 safari version"
        ]
      },
      engines: {
        node: ">=18.0"
      }
    };

    writeFileSync(
      join(websiteDir, 'package.json'),
      JSON.stringify(packageJsonContent, null, 2)
    );

    // Install dependencies
    console.log('📦 Installing npm dependencies...');
    const installResult = spawnSync('npm', ['install'], {
      cwd: websiteDir,
      stdio: 'inherit',
    });

    if (installResult.status !== 0) {
      console.error('❌ Failed to install dependencies');
      process.exit(1);
    }
  }
} catch (error) {
  console.error('❌ Error checking Docusaurus:', error);
}

// Generate OpenAPI specification from backend
console.log('📡 Generating OpenAPI specification...');
const openapiPath = join(websiteDir, 'static/openapi.json');

// For now, create a minimal OpenAPI spec as placeholder
const openapiSpec = {
  openapi: "3.1.0",
  info: {
    title: "OpenDomain API",
    version: "0.1.0",
    description: "Open-source domain registrar platform with integrated AI agent"
  },
  servers: [
    {
      url: "https://api.opendomain.dev/api/v1",
      description: "Production API"
    },
    {
      url: "http://localhost:8000/api/v1",
      description: "Local development"
    }
  ],
  paths: {},
  components: {}
};

writeFileSync(openapiPath, JSON.stringify(openapiSpec, null, 2));

// Build Docusaurus site
console.log('🏗️ Building Docusaurus site...');
const buildResult = spawnSync('npm', ['run', 'build'], {
  cwd: websiteDir,
  stdio: 'inherit',
});

if (buildResult.status === 0) {
  console.log('✅ Documentation site built successfully!');
  console.log('');
  console.log('To preview the site:');
  console.log('  cd website && npm run serve');
  console.log('');
  console.log('To develop locally:');
  console.log('  cd website && npm start');
} else {
  console.error('❌ Failed to build documentation site');
  process.exit(1);
}