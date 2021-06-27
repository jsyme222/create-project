#!/usr/bin/python3.9

import os
from posixpath import relpath
import sys
import getopt
import random
import subprocess
import fileinput
from pathlib import Path


class Project():
    '''Represents a project directory

    Attributes:
    -----------
    title : str
        Title of project
    location : str
        Directory location of project

    Methods:
    --------
    set_title()
        takes 2 random words and builds a single title;
    create_directory()
        create the given location if not exists;
    create_project()
        create project skeleton within location;
    '''

    def __init__(self, title: str = None, location: str = None, options: dict = {}) -> None:
        self.title = title
        self.location = location or "/home/jsyme/projects/"
        self.react_app = False if "react-app" not in options.keys() else True

    def set_title(self):
        word_file = "/usr/share/dict/words"
        WORDS = open(word_file).read().splitlines()

        def random_word():
            wrd = random.choice(WORDS)
            return "".join(w for w in wrd if w.isalnum()).lower()
        self.title = f'{random_word()}-{random_word()}'

    def create_directory(self):
        # If the project location is not a dir it will be created
        path = f'{os.path.realpath(self.location)}'
        create = input(f'Create: {path} ?  \n[y/n] ')
        if create.lower() in ["y", "yes"]:
            print(f'Creating location: {path}')
            os.makedirs(path)
        print(f'Creating {path}')

    def create_react_app(self):
        # Creates a react typescript skeleton
        path = Path(self.location, self.title)
        if not os.path.isdir(path):
            os.mkdir(path)  # Create project root
        os.chdir(path)  # Change to project root

        def yarn_install():
            # install package.json
            yarn = subprocess.Popen(
                ["yarn"])
            yarn_output, yarn_error = yarn.communicate()
            if yarn_error:
                print(yarn_error)
                raise SystemError
            print(yarn_output)

        def yarn_cra():
            # create-react-app typescript app
            cra = subprocess.Popen(
                ["yarn", "create", "react-app", "app", "--template", "typescript"])
            cra_output, cra_error = cra.communicate()
            if cra_error:
                print(cra_error)
                raise SystemError
            print(cra_output)

        def create_project_folders():
            print("\nCreating React Folders:\n")
            src = Path("app", "src")
            os.chdir(src)
            folders = [
                Path("ts", "components"),
                Path("ts", "types"),
                Path("data", "db"),
                Path("assets", "css"),
                Path("assets", "img")
            ]
            for folder in folders:
                print(folder)
                os.makedirs(folder)

        def yarn_deps():
            print("\nInstalling Dependencies")
            deps = subprocess.Popen(
                ["yarn", "add", "node-sass@4.14.1", "jotai"]
            )
            deps_output, deps_error = deps.communicate()
            if deps_error:
                print(deps_error)
                raise SystemError
            print(deps_output)

            # Prep css for scss
            create_project_folders()

            files_to_change = os.listdir()
            for file in files_to_change:
                if file.endswith(".css"):
                    # Rename to scss and move to assets/css directory
                    print("Altering:")
                    print(file)
                    os.rename(file, "assets/css/" +
                              file.split(".")[0] + ".scss")
                elif os.path.isfile(file):
                    # Find and replace any instance of css vs scss
                    with fileinput.FileInput(file, inplace=True) as f:
                        for line in f:
                            if ".css" in line:
                                l = line.split("/")
                                line = l[0] + "/assets/css/" + l[-1]
                                print(line.replace(".css", ".scss"), end=" ")
                            else:
                                print(line)

        def create_dockerfile():
            root_dir = Path(self.location, self.title, "app")
            os.chdir(root_dir)
            docker_commands = """FROM node:14\nWORKDIR /app\nENV PATH /app/node_modules/.bin:$PATH\nCOPY package.json ./\nCOPY yarn.lock ./\nRUN yarn install --silent\nRUN yarn global add react-scripts@4.0.3\nCOPY . /app/"""

            with open("Dockerfile", "w") as Dockerfile:
                Dockerfile.write(docker_commands)
                print("Dockerfile Created")

        yarn_install()
        yarn_cra()
        yarn_deps()
        create_dockerfile()

    def create_project(self):
        try:
            if not self.title:
                # set random title if not provided
                self.set_title()
            if not os.path.isdir(self.location):
                # create path for project root
                self.create_directory()
            print(f'Creating {self.title} in {self.location}')
            if self.react_app:
                try:
                    self.create_react_app()
                except SystemError:
                    print("ERROR: creating react app")
                    return

            exit

        except KeyboardInterrupt:
            print("\nAdios!\n")


def get_args() -> dict:
    payload = {"options": {}}
    argument_list = sys.argv[1:]
    opts = "rn:l:h"
    try:
        arguments, values = getopt.getopt(argument_list, opts)

        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h"):
                print("Diplaying Help")

            elif currentArgument in ("-r"):
                payload["options"] = {
                    **payload["options"],
                    "react-app": True
                }

            elif currentArgument in ("-n"):
                payload["title"] = currentValue

            elif currentArgument in ("-l"):
                payload["location"] = currentValue

    except getopt.error as err:
        print(str(err))

    return payload


if __name__ == "__main__":
    args = get_args()
    p = Project(**args).create_project()
