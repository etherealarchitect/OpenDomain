// @ts-check
const {themes} = require('@docusaurus/theme-classic');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'OpenDomain',
  tagline: 'Open-source domain registrar platform with integrated AI agent',
  url: 'https://docs.opendomain.dev',
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'etherealarchitect',
  projectName: 'OpenDomain',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/plugin-content-docs').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/etherealarchitect/OpenDomain/tree/main/website/',
          routeBasePath: '/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
    [
      'docusaurus-preset-openapi',
      {
        api: {
          path: 'static/openapi.json',
          routeBasePath: '/api',
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/theme-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'OpenDomain Docs',
        logo: {
          alt: 'OpenDomain Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            to: '/getting-started',
            label: 'Getting Started',
            position: 'left',
          },
          {
            to: '/api',
            label: 'API Reference',
            position: 'left',
          },
          {
            to: '/cli',
            label: 'CLI',
            position: 'left',
          },
          {
            to: '/deployment',
            label: 'Deployment',
            position: 'left',
          },
          {
            href: 'https://github.com/etherealarchitect/OpenDomain',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Getting Started',
                to: '/getting-started',
              },
              {
                label: 'API Reference',
                to: '/api',
              },
              {
                label: 'CLI Guide',
                to: '/cli',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Issues',
                href: 'https://github.com/etherealarchitect/OpenDomain/issues',
              },
              {
                label: 'Discussion',
                href: 'https://github.com/etherealarchitect/OpenDomain/discussions',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/etherealarchitect/OpenDomain',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Ethereal Architect. Built with Docusaurus.`,
      },
      prism: {
        theme: themes.prism.github,
        darkTheme: themes.prism.dracula,
        additionalLanguages: ['bash', 'json', 'python', 'typescript'],
      },
    }),
};

module.exports = config;