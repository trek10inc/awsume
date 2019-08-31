module.exports = {
  title: 'AWSume',
  description: 'Awsume - A cli that makes using AWS IAM credentials easy',
  base: '/',
  themeConfig: {
    lastUpdated: 'Last Updated', // string | boolean
  },
  plugins: [
    [
      '@vuepress/google-analytics',
      {
        'ga': 'UA-47115220-9',
      }
    ]
  ],
  themeConfig: {
    displayAllHeaders: true,
    sidebarDepth: 0,
    logo: '/logo.png',
    nav: [
      { text: 'Home', link: '/' },
      { text: 'GitHub', link: 'https://github.com/trek10inc/awsume' },
      { text: 'Trek10', link: 'https://trek10.com' },
    ],
    sidebar: [
      ['/', 'AWSume'],
      {
        title: 'General',
        collapsable: true,
        children: [
          '/general/quickstart',
          '/general/overview',
          '/general/aws-file-configuration',
          '/general/usage',
          '/general/config',
        ],
      },
      {
        title: 'Utilities',
        collapsable: true,
        children: [
          '/utilities/awsume-configure',
        ],
      },
      {
        title: 'Advanced',
        collapsable: true,
        children: [
          '/advanced/autoawsume',
          '/advanced/region',
          '/advanced/role-duration',
          '/advanced/external-id',
          '/advanced/fuzzy-matching',
        ],
      },
      {
        title: 'Plugins',
        collapsable: true,
        children: [
          '/plugins/',
        ],
      },
      {
        title: 'Plugins Development',
        collapsable: true,
        children: [
          '/plugin-development/',
          '/plugin-development/add-arguments',
          '/plugin-development/collect-aws-profiles',
          '/plugin-development/get-credentials',
          '/plugin-development/get-profile-names',
          '/plugin-development/catch-exceptions',
        ],
      },
      {
        title: 'Updating to v4',
        collapsable: true,
        children: [
          '/updating-v4/',
        ],
      },
      {
        title: 'Troubleshooting',
        collapsable: true,
        children: [
          '/troubleshooting/',
        ],
      },
      {
        title: 'Changelog',
        collapsable: true,
        children: [
          '/changelog',
        ],
      },
    ],
  },
};
