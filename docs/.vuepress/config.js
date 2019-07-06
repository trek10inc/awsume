module.exports = {
  title: 'AWSume',
  description: 'Awsume - A cli that makes using AWS IAM credentials easy',
  base: '/',
  themeConfig: {
    lastUpdated: 'Last Updated', // string | boolean
  },
  themeConfig: {
    displayAllHeaders: true,
    // sidebarDepth: 1,
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
          '/general/aws-file-configuration',
          '/general/usage',
          '/general/overview',
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
        ],
      },
      // {
      //   title: 'Plugins',
      //   collapsable: true,
      //   children: [
      //     '/plugins/',
      //     '/plugins/profiles',
      //   ],
      // },
    ],
  },
};
