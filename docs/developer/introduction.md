# Awsume's Developer Documentation

Welcome to Awsume's developer documentation. This is where you can find information around how the Awsume code-base is structured, to hopefully make development on the project easier.

Awsume is written as a command-line tool in Python, so most conventional Python standards are followed.

## Project Layout

- `awsume` - the main package for the awsume application
- `awsume_autocomplete` - a peripheral pacakge used to make awsume's autocomplete on plugin-supplied profiles a lot faster
- `docs` - the VuePress documentation location - what you're reading right now!
- `shell_scripts` - the location of the shell script wrappers that are used to wrap the `awsumepy` executable for a given shell. This allows `source`ing the shell script so your active shell's AWS environment variables can be set
- `test` - the location of awsume's test files

It's environment has been described in the `Pipfile`, with some scripts that can help facilitate your development.

---

It's helpful to be familiar with the following when developing for awsume:

- Python development:
  - Virtualenvironments (including [pipenv](https://docs.pipenv.org/))
  - The `setup.py` file (setuptools)
  - [pytest](https://docs.pytest.org/en/stable/)
  - Modules and packages
- Unit testing and module/function mocking
- Plugin Systems
  - [`pluggy`](https://pluggy.readthedocs.io/en/latest/)
  - Awsume's [plugin development](/plugin-development) process
- AWS
  - IAM users and roles
  - STS credentials
  - Boto3
  - [Shared Credentials and Config files](https://ben11kehoe.medium.com/aws-configuration-files-explained-9a7ea7a5b42e)
