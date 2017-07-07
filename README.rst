AWSume: AWS Assume Made Awesome
===============================

Utility for easily assuming AWS IAM roles from the command line, now in
Python!

What is AWSume?
---------------

AWSume is a cross-platform (Mac, Linux, Windows) command-line tool that
makes assuming AWS roles and setting user credentials from the AWS CLI
easy! It works by scanning your ``.aws/config`` and ``.aws/credentials``
files for the profile you give it, making AWS calls to get that
profile's credentials, and exporting those credentials to your shell's
environment variables. Then, any AWS CLI calls you make in that shell
will be under the profile you gave AWSume.

Now, AWSume comes with a built-in auto-refresher! AWS role credentials
are only valid for an hour max, and once that hour is up, you need to
refresh those credentials, either by calling AWSume again, or doing it
yourself. Now, AWSume has the ability to spawn a background process that
waits for your role credentials to expire, and auto-refreshes them for
you, that is, for as long as the role's source profile is valid. And
when you're done working with that role and you'd like to stop that
background process from refreshing those role credentials, simply pass
the ``-k`` flag with the profile you gave it to AWSume. If you're done
working with all auto-refreshed roles entirely, you can just call
``awsume -k`` without a profile to kill the background process and
remove those role credentials.

Installation
------------

Pip Installation
~~~~~~~~~~~~~~~~

AWSume has been conveniently wrapped into a Python package and
installable with just one simple command:

``pip install awsume``

This will install AWSume from from the Python Package Index. The
installer places the python and shell scripts into your python
directory. If you're using ``Bash`` or ``Zsh``, the installer will add
an alias definition to their resource control file, either
``.bash_alias``, ``.bashrc``, ``.bash_profile``, or ``.zshrc``. When
uninstalling AWSume, the alias definition will not be removed.

Once you have AWSume installed, you're ready to set up AWSume!

NOTES
^^^^^

-  You must have Python and Pip installed in order to use AWSume. Get
   them `here <https://www.python.org>`__.
-  Make sure your Python PATH environment variables are set.
-  For Linux / macOS users, restart your terminal after installing to
   ensure the alias to AWSume is active.
- For macOS users, you may have to run pip with the
  ``--ignore-installed six`` option. Try installing without it first.
  If it doesn't work, try adding the option to the end of the command.

Setup
-----

Configuring Using The AWS CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``aws configure set <key> <value> --profile <profile_name>``

Where:

-  ``key`` is what you would like to set within the
   ``config``/``credentials`` file, such as:
-  ``aws_access_key_id``, ``aws_secret_access_key``, ``region``,
   ``output``, ``mfa_serial``, ``role_arn``, or ``source_profile``
-  ``value`` is the value you'd like to set the ``key`` to
-  ``profile_name`` is the name of the profile you are creating
-  ``profile_name`` is what you will pass into AWSume

Configuring Manually
~~~~~~~~~~~~~~~~~~~~

Add profiles to

``~/.aws/config`` (for macOS / Linux)

``%userprofile%\.aws\config`` (for Windows)

Add source profiles to

``~/.aws/credentials`` (for macOS / Linux)

``%userprofile%\.aws\credentials`` (for Windows)

~/.aws/config
^^^^^^^^^^^^^

::

    [default]
    region = us-east-1
    [profile internal-admin]
    role_arn = arn:aws:iam::<your aws account id>/role/admin-role
    source_profile = joel
    region = us-east-1
    [profile client1-admin]
    role_arn = arn:aws:iam::<client #1 account id>/role/admin-role
    mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
    source_profile = joel
    region = us-west-2
    [profile client2-admin]
    role_arn = arn:aws:iam::<client #2 account id>/role/admin-role
    mfa_serial = arn:aws:iam::<your aws account id>:mfa/joel
    source_profile = joel
    region = us-east-1

Add credentials to

``~/.aws/credentials`` (for macOS / Linux)

``%userprofile%\.aws\credentials`` (for Windows)

~/.aws/credentials
^^^^^^^^^^^^^^^^^^

::

    [default]
    aws_access_key_id = AKIAIOIEUFSN9EXAMPLE
    aws_secret_access_key = wJalrXIneUATF/K7MDENG/jeuFHEnfEXAMPLEKEY
    [joel]
    aws_access_key_id = AKIAIOSFODNN7EXAMPLE
    aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

Usage:
------

::

    usage: awsumepy [-h] [-d] [-s] [-r] [-a] [-k] [-v] [-l] [profile name]

    AWSume

    positional arguments:
    profile name  The profile name

    optional arguments:
    -h, --help    show this help message and exit
    -d            Use the default profile
    -s            Show the commands to assume the role
    -r            Force refresh the session
    -a            Enable auto-refreshing role credentials
    -k            Kill the auto-refreshing process
    -v            Display the current version of AWSume
    -l            List useful information about available 

AutoAwsume
~~~~~~~~~~

AutoAwsume is a new feature that brings in the ability to auto-refresh
your role credentials, so that you don't have to worry about refreshing
them yourself every hour. Lets say you want to work under your
``client-admin`` role, whose source profile is ``client-source``. If you
want to AWSume ``client-admin`` credentials, but want them to be
auto-refreshed when they expire, simply call ``awsume client-admin -a``.

Then, AWSume will add an ``auto-refresh-client-admin`` profile to your
``.aws/credentials`` file, and export that profile to your environment's
``AWS_PROFILE`` and ``AWS_DEFAULT_PROFILE`` variables. Then, any AWS
calls you make will be under that profile.

Now, while that is happening, AWSume spawned a background process,
``autoAwsume``, that scanns through all profiles listed in your
``.aws/credentials`` file, and finds any that are prefixed with
``auto-refresh-``. (In this case, it'd find a profile named
``auto-refresh-client-admin``) AutoAwsume finds the credentials that
will expire the soonest (whether that be the role's source profile
credentials or the role credentials themselves) and waits for that
moment before it runs again to refresh it.

When you're ready to stop working on that profile, simply call
``awsume client-admin -k`` to remove the ``auto-refresh-client-admin``
profile from your ``.aws/credentials`` file. If there are no more
``auto-refresh-`` profiles remaining in your ``.aws/credentials`` file,
autoAwsume will stop running. If you'd like to stop autoAwsume entirely
and remove all ``auto-refresh-`` profiles from the ``.aws/credentials``
file completely, simply call ``awsume -k``.

NOTES
^^^^^

-  Do not kill the autoAwsume process yourself, only kill it through the
   ``awsume [profile] -k`` command.
-  When working with autoAwsume on Windows, if you're using Command
   Prompt, autoAwsume will appear as a minimized window. Only shut it
   down with the ``awsume [profile] -k`` command.
-  When working on Windows, use the same shell to shut autoAwsume down
   that you used to start it up. Do not try to close the autoAwsume
   process with PowerShell if it has been started with Command Prompt,
   and vise versa.
-  AutoAwsume works using the ``AWS_PROFILE`` and
   ``AWS_DEFAULT_PROFILE`` environment variables that point to a
   specific profile in your ``.aws/credentials`` file, so when that
   profiles' source profile credentials expire (They usually last around
   12 hours), you may get an error telling you that
   ``The config profile ([profile]) could not be found``. If this
   happens just call AWSume again to continue working.

Examples:
~~~~~~~~~

``awsume client1-source-profile`` Exports ``client1-source-profile``
credentials into current shell, will ask for MFA if needed

``awsume client1-source-profile -n`` Exports ``client1-source-profile``
credentials into current shell, will usually not ask for MFA, but it
will if ``client1-source-profile`` is a role profile instead of a source
profile, and requires MFA

``awsume client1-admin`` Exports ``client1-admin`` credentials into
current shell, will ask for MFA if needed

``awsume`` Exports the default profile's credentials into current shell,
will ask for MFA if needed

``awsume -d`` Exports the default profile's credentials into current
shell, will ask for MFA if needed

``awsume client1-admin -s`` Outputs export commands to shell, useful if
you want to copy / paste into some other shell, will ask for MFA if
needed

``awsume client1-admin -r`` Delete cached credentials and refresh, will
always prompt for MFA.

``awsume client1-admin -a`` Exports auto-refresh profile to shell's
``AWS_DEFAULT_PROFILE`` and ``AWS_PROFILE`` environment variables,
creates a profile in the ``.aws/credentials`` file called
``auto-refresh-client1-admin`` that contains profile's role credentials,
and spawns a background process to auto-refresh those role credentials
when they expire, for as long as the role's source profile is valid.

``awsume client1-admin -k`` Removes the ``auto-refresh-client1-admin``
profile from the ``.aws/credentials`` file. If no more ``auto-refresh-``
profiles are left in the ``.aws/credentials`` file, the auto-refreshing
background process will be killed.

``awsume -k`` Removes all ``auto-refresh-`` profiles from the
``.aws/credentials`` file, and kills the auto-refreshing background
process.

NOTES
^^^^^

-  Only use the ``awsume [profile] -k`` option to stop the background
   process, do not run a ``kill`` command or terminate the process
   yourself without AWSume.

See our
`blog <https://www.trek10.com/blog/awsume-aws-assume-made-awesome>`__
for more details.
