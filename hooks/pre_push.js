const fs = require('fs');
const parameters = JSON.parse(fs.readFileSync(0, { encoding: 'utf8' }));

// Get the running Amplify CLI major version number
const currentCLIMajorVersion = parameters.data.amplify.version.split('.')[0]
console.log('Amplify CLI major version: ', currentCLIMajorVersion)

const MINIMUM_MAJOR_AMPLIFY_CLI_VERSION = 5
console.log('Minimum required Amplify CLI major version: ', MINIMUM_MAJOR_AMPLIFY_CLI_VERSION)

if (currentCLIMajorVersion < MINIMUM_MAJOR_AMPLIFY_CLI_VERSION) {
    // Non-zero exit code will stop the Amplify CLI command's execution
    console.log('Minimum CLI version requirement not met.')
    process.exit(1)
} else {
    console.log('Minimum CLI version requirement met.')
    process.exit(0)
}
