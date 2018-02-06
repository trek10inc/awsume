import atexit, os, subprocess
import urllib
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.install_scripts import install_scripts
from distutils.spawn import find_executable

version = '2.1.5'

class CustomInstall(install):

    #the auto-complete scripts
    bashScript = """_awsume() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts=$(awsumepy --rolesusers)
    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _awsume awsume"""

    zshScript = """#compdef awsume
_arguments "*: :($(awsumepy --rolesusers))" """

    powershellScript = """Register-ArgumentCompleter -Native -CommandName awsume -ScriptBlock {
    param($wordToComplete, $commandAst, $cursorPosition)
    $(awsumepy --rolesusers) |
    Where-Object { $_ -like "$wordToComplete*" } |
    Sort-Object |
    ForEach-Object {
        [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_)
    }
}"""

    def get_bash_file(self, homefolder):
        # default rc_file
        rc_file = os.path.abspath('%s/.profile' % homefolder)
        if os.path.exists(os.path.abspath('%s/.bash_aliases' % homefolder)):
            rc_file = os.path.abspath('%s/.bash_aliases' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.bashrc' % homefolder)):
            rc_file = os.path.abspath('%s/.bashrc' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.bash_profile' % homefolder)):
            rc_file = os.path.abspath('%s/.bash_profile' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.login' % homefolder)):
            rc_file = os.path.abspath('%s/.login' % homefolder)
        return rc_file

    def get_zsh_file(self, homefolder):
        # default
        rc_file = os.path.abspath('%s/.zprofile' % homefolder)
        if os.path.exists(os.path.abspath('%s/.zshrc' % homefolder)):
            rc_file = os.path.abspath('%s/.zshrc' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.zshenv' % homefolder)):
            rc_file = os.path.abspath('%s/.zshenv' % homefolder)
        elif os.path.exists(os.path.abspath('%s/.zlogin' % homefolder)):
            rc_file = os.path.abspath('%s/.zlogin' % homefolder)
        return rc_file

    def add_alias(self, rc_file, alias):
        with open(rc_file, 'a+') as read_f:
            lines = read_f.readlines()
            if alias not in lines:
                out = open(rc_file, 'a')
                out.write("\n#AWSume alias to source the AWSume script\n")
                out.write(alias)
                out.close()

    def add_bash_script(self, rc_file, bashScript):
        with open(rc_file, 'a+') as read_f:
            content = read_f.read()
            if not bashScript in content:
                out = open(rc_file, 'a')
                out.write('\n#Auto-Complete function for AWSume')
                out.write('\n' + bashScript + '\n')
                out.close()

    def add_zsh_script(self, zsh_script, rc_file, func_dir):
        #if /usr/local/share/zsh/site-functions doesn't exist, add it
        if not os.path.exists(func_dir):
            os.makedirs(func_dir)
            #add the directory to fpath
            with open(rc_file, 'r') as original: data = original.read()
            with open(rc_file, 'w') as modified: modified.write('fpath=$(' + func_dir + ' $fpath)\n' + data)

        #add _awsume completion function to site-functions directory
        func_file = func_dir + '/_awsume'
        with open(func_file, 'w+') as f:
            content = f.read()
            if not zsh_script in content:
                out = open(func_file, 'a')
                out.write(zsh_script + '\n')
                out.close()

    def add_powershell_script(self, script, powershell_file):
        contents = open(powershell_file, 'w+').read()
        if script not in contents:
            f = open(powershell_file, 'a+')
            f.write('\n' + script + '\n')
            f.close()

    def run(self):
        def _post_install():
            #cross platform home folder
            homefolder = os.path.expanduser('~')

            #alias string to add
            alias = 'alias awsume=". awsume"\n'

            #pyenv compatibility
            if find_executable('pyenv'):
                pyenv_version = os.popen('pyenv version').read().split('(')[0].strip()
                alias = 'alias awsume=". ~/.pyenv/versions/' + pyenv_version + '/bin/awsume"'

            # add bash alias/script, add alias to bash file
            # regardless of platform for compatibility
            rc_file = self.get_bash_file(homefolder)
            self.add_alias(rc_file, alias)
            self.add_bash_script(rc_file, self.bashScript)

            #add zsh alias/script
            if find_executable('zsh'):
                rc_file = self.get_zsh_file(homefolder)
                fpath_dir = os.path.abspath('/usr/local/share/zsh/site-functions')
                self.add_alias(rc_file, alias)
                self.add_zsh_script(self.zshScript, rc_file, fpath_dir)

            #add powershell script
            if find_executable('powershell'):
                (file_name, err) = subprocess.Popen(["powershell", "$profile"], stdout=subprocess.PIPE, shell=True).communicate()
                file_name = str(file_name.decode('ascii')).replace('\r\n', '')
                self.add_powershell_script(self.powershellScript, file_name)

        atexit.register(_post_install)
        install.run(self)

class CustomInstallScripts(install_scripts):
    def run(self):
        def _post_install_scripts():
            #make sure awsume is executable
            execpath = '/usr/local/bin/awsume'
            if os.path.exists(execpath):
                os.chmod(execpath, int('755', 8))
        atexit.register(_post_install_scripts)
        install_scripts.run(self)

setup(
    name="awsume",
    packages=find_packages(exclude=("*test*", "./awsume/test*", "./awsume/testAwsume.py")),
    version=version,
    author="Trek10, Inc",
    author_email="package-management@trek10.com",
    description="Utility for easily assuming AWS IAM roles from the command line, now in Python!",
    long_description=open('README.rst').read(),
    license="MIT",
    url='https://github.com/trek10inc/awsume',
    download_url='https://github.com/trek10inc/awsume/archive/' + version + '.tar.gz',
    scripts=[
        'awsume/shellScripts/awsume',
        'awsume/shellScripts/awsume.ps1',
        'awsume/shellScripts/awsume.bat',
    ],
    include_package_data=True,
    install_requires=[
        'python-dateutil',
        'boto3',
        'psutil',
        'yapsy',
        'future'
    ],
    entry_points={
        "console_scripts": [
            'awsumepy=awsume.awsumepy:main',
            'autoAwsume=awsume.autoAwsume:main'
        ]
    },
    cmdclass={
        'install': CustomInstall,
        'install_scripts': CustomInstallScripts,
    },
)
