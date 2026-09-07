import {themes as prismThemes} from "prism-react-renderer";
import type {Config} from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: "{{ package_name | default("My Site") | safe }}",
  tagline: "Dinosaurs are cool",
  favicon: "img/favicon.ico",

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: "https://{{ user | default("username") | safe }}.github.io",
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: "/{{ package_name | default("pkgname") | safe }}/",

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: "{{ user | default("username") | safe }}", // Usually your GitHub org/user name.
  projectName: "{{ package_name | default("pkgname") | safe }}", // Usually your repo name.

  onBrokenLinks: "throw",
  trailingSlash: false,

  plugins: [
    [
      // Use SASS/SCSS.
      "docusaurus-plugin-sass",
      {
        // options
        // api: "modern-compiler",
      },
    ],
  ],

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            "https://github.com/{{ user | default("username") | safe }}/{{ package_name | default("pkgname") | safe }}/edit/docs/",
          editLocalizedFiles: true,
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ["rss", "atom"],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            "https://github.com/{{ user | default("username") | safe }}/{{ package_name | default("pkgname") | safe }}/edit/blog/",
          // Useful options to enforce blogging best practices
          onInlineTags: "warn",
          onInlineAuthors: "warn",
          onUntruncatedBlogPosts: "warn",
        },
        theme: {
          customCss: "./src/css/custom.scss",
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: "img/docusaurus-social-card.jpg",
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "{{ package_name | default("My Site") | safe }}",
      logo: {
        alt: "{{ package_name | default("My Site") | safe }} Logo",
        src: "img/logo.svg",
      },
      hideOnScroll: false,
      items: [
        {
          type: "docSidebar",
          sidebarId: "tutorialSidebar",
          position: "left",
          label: "Tutorial",
        },
        {
          type: "docSidebar",
          sidebarId: "apis",
          position: "left",
          label: "APIs",
        },
        {to: "/blog", label: "Blog", position: "left"},
        {
          href: "https://github.com/{{ user | default("username") | safe }}/{{ package_name | default("pkgname") | safe }}",
          position: "right",
          className: "header-github-link",
          "aria-label": "GitHub repository",
        },
        {
          href: "https://pypi.org/project/{{ package_name | default("pkgname") | as_pypi_name | safe }}",
          position: "right",
          className: "header-pypi-link",
          "aria-label": "PyPI repository",
        }
      ],
    },
    footer: {
      style: "dark",
      links: [
        {
          title: "Docs",
          items: [
            {
              label: "Tutorial",
              to: "/docs/",
            },
            {
              label: "APIs",
              to: "/docs/",
            },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "Stack Overflow",
              href: "https://stackoverflow.com/questions/tagged/{{ package_name | default("pkgname") | safe }}",
            },
            {
              label: "Discord",
              href: "https://discordapp.com/invite/{{ package_name | default("pkgname") | safe }}",
            },
            {
              label: "X",
              href: "https://x.com/{{ package_name | default("pkgname") | safe }}",
            },
          ],
        },
        {
          title: "More",
          items: [
            {
              label: "Blog",
              to: "/blog",
            },
            {
              label: "GitHub",
              href: "https://github.com/{{ user | default("username") | safe }}/{{ package_name | default("pkgname") | safe }}",
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} {{ user | default("username") | safe }}. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ["bash", "python"],
      magicComments: [
        // Remember to extend the default highlight class name as well!
        {
          className: "theme-code-block-highlighted-line",
          line: "highlight-next-line",
          block: {start: "highlight-start", end: "highlight-end"},
        },
        {
          className: "code-block-error-line",
          line: "This will error",
        },
      ],
    },
    docs: {
      sidebar: {
        hideable: true,
        autoCollapseCategories: true,
      },
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
