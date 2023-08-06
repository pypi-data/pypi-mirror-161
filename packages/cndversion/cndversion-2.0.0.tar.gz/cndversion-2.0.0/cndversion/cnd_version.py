from .__version__ import (
    __version__,
)
import sys
import os


class CndVersion:
    def __init__(self, arguments):
        print(f"Cndvops Version {__version__}")
        self.arguments = arguments

    def increment(self):
        version = self.current_version()
        initial_version = f"{version[0]}.{version[1]}.{version[2]}"
        print(f"Current version : {initial_version}")
        if self.arguments.folder:
            print("VERSION file already active, skipping")
            return None
        if self.arguments.major:
            position = 0
        if self.arguments.minor:
            position = 1
        if self.arguments.patch:
            position = 2
        version[position] += 1
        for x in range(2 - position):
            version[x + position + 1] = 0
        version_txt = f"{version[0]}.{version[1]}.{version[2]}"
        open(self.path, 'w').write(version_txt)
        print(f"New version is now : {version_txt}")
        os.system(f"echo 'Version {version_txt}: ' > tmpfile")
        os.system(f'git log --pretty=format:" - %s" "v{initial_version}"...HEAD >> tmpfile')
        os.system(f"echo '' >> tmpfile")
        os.system(f"echo '' >> tmpfile")
        os.system('cat CHANGES >> tmpfile')
        os.system('mv tmpfile CHANGES')
        os.system(f'git add CHANGES VERSION {self.path}')
        os.system(f'git commit -m "Version bump to {version_txt}"')
        os.system(f'git tag -a -m "Tagging version $INPUT_STRING" "v{version_txt}"')
        os.system('git push origin --tags')

    def valid_version_number(self, number):
        m = number.split('.')
        if len(m) == 3:
            return True
        return False

    def _build_init(self, folder):
        self.create_file_if_not_exist(f'{folder}/__init__.py', '\n')
        init_content = "from .__version__ import (__version__)  # noqa: F401\n"
        with open(f'{folder}/__init__.py', 'r+') as file:
            content = file.read()
            file.seek(0)
            file.write(init_content + content)

    def create_file_if_not_exist(self, filename, content):
        if os.path.exists(filename) is True:
            print(f"File {filename} already exists... skipping")
        open(filename, 'w').write(content)

    def _create_base(self):
        if self.arguments.folder is not False:
            path = self.arguments.folder
        else:
            path = input("What is your lib folder ? ")
        if path != None:
            if os.path.exists(path) is False:
                os.mkdir(path)
            self._build_init(path)
            version_content = 'import pkg_resources\n\n\npath = pkg_resources.resource_filename("{path}", "VERSION")\n__version__ = open(path).read()\n'
            self.create_file_if_not_exist(f'{path}/__version__.py', version_content)
        self.create_file_if_not_exist('VERSION', f'{path}/VERSION')
        self.create_file_if_not_exist(f'{path}/VERSION', '0.1.0')
        self.create_file_if_not_exist('CHANGES', '')
        os.system('git log --pretty=format:" - %s" >> CHANGES')
        os.system(f'git add CHANGES VERSION')
        os.system('git commit -m "Added VERSION and CHANGES files, Version bump to v0.1.0"')
        os.system('git tag -a -m "Tagging version 0.1.0" "v0.1.0"')
        os.system('git push origin --tags')
        sys.exit()

    def find_version_file(self):
        if os.path.isfile('VERSION') is False:
            print("Could not find a VERSION file")
            my_input = input("Do you want to create a version file and start from scratch? [y] ")
            if my_input.lower() in ['y', '', 'yes']:
                self._create_base()
            else:
                print('Nothing created, bye')
                sys.exit()
        path = open('VERSION').read().strip()
        valid_version = self.valid_version_number(path)
        if valid_version is True:
            return 'VERSION'
        if os.path.exists(path) is True:
            print("PATH EXISTS")
            return path
        raise ValueError("NotValid")

    def current_version(self):
        self.path = self.find_version_file()
        version_content = open(self.path).read()
        m = version_content.split('.')
        return [int(m[0]), int(m[1]), int(m[2])]
