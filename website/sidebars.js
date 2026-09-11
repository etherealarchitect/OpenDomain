/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    {
      type: 'doc',
      label: 'Introduction',
      id: 'introduction',
    },
    {
      type: 'category',
      label: 'Getting Started',
      collapsed: false,
      items: [
        'getting-started/quick-start',
        'getting-started/architecture',
        'getting-started/authentication',
        'getting-started/first-domain',
      ],
    },
    {
      type: 'category',
      label: 'API',
      collapsed: false,
      items: [
        'api/overview',
        'api/authentication',
        'api/domains',
        'api/dns',
        'api/contacts',
        'api/agent',
        'api/billing',
        'api/monitoring',
      ],
    },
    {
      type: 'category',
      label: 'CLI',
      collapsed: false,
      items: [
        'cli/installation',
        'cli/authentication',
        'cli/domains',
        'cli/dns',
        'cli/agent',
        'cli/advanced-usage',
      ],
    },
    {
      type: 'category',
      label: 'Deployment',
      collapsed: false,
      items: [
        'deployment/local-development',
        'deployment/docker-compose',
        'deployment/vultr-vps',
        'deployment/production-checklist',
        'deployment/monitoring',
      ],
    },
    {
      type: 'category',
      label: 'Developer Guide',
      collapsed: false,
      items: [
        'development/setup',
        'development/adding-endpoints',
        'development/testing',
        'development/contributing',
        'development/release-process',
      ],
    },
  ],
};

module.exports = sidebars;