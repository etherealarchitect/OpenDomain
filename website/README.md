# OpenDomain Documentation Website

This is the documentation website for OpenDomain, built with Docusaurus.

## Quick Start

```bash
cd website
npm install
npm start
```

## Building

Build the static site:

```bash
npm run build
```

The built site will be in the `build/` directory.

## Deploying

Deploy to GitHub Pages:

```bash
npm run deploy
```

## Features

- **Docusaurus 3**: Modern documentation framework
- **OpenAPI Integration**: API documentation from OpenAPI spec
- **Search**: Built-in search functionality
- **Dark/Light Mode**: Theme switching
- **Responsive Design**: Mobile-friendly documentation

## Content Structure

- `docs/` - Documentation files
- `static/` - Static assets (images, OpenAPI spec)
- `src/` - Custom React components and CSS

## Development

- Edit documentation in `docs/`
- Add custom components in `src/components/`
- Update navigation in `sidebars.js`
- Configure the site in `docusaurus.config.js`

## Updating OpenAPI Spec

To update the OpenAPI specification:

1. Generate the OpenAPI spec from the backend:

```bash
cd ../backend
python -c "from backend.app.main import app; import json; with open('../website/static/openapi.json', 'w') as f: json.dump(app.openapi(), f, indent=2)"
```

2. The build process will include the updated spec automatically.

## Contributing

Documentation contributions are welcome! Please see the main project's [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.