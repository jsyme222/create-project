#!/usr/bin/python3.9

from config import PROJECT_ROOT
from docker.services import COMPOSE, DOCKERFILE
import os
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
        self.location = location or PROJECT_ROOT
        self.options = options
        self.dockercompose = None
        self.root_dir = Path(self.location, self.title)

    def set_title(self):
        word_file = "/usr/share/dict/words"
        WORDS = open(word_file).read().splitlines()

        def random_word():
            # Create a random 2 word title
            wrd = random.choice(WORDS)
            return "".join(w for w in wrd if w.isalnum()).lower()

        title = f'{random_word()}-{random_word()}'

        accepted = input(f'Accept title: {title}\n[y/n]')
        if accepted.lower() in ["y", "yes"]:
            self.title = title
        else:
            self.set_title()

    def create_directory(self, dir):
        # If the project location is not a dir it will be created
        path = f'{os.path.realpath(dir)}'
        create = input(f'Create: {path} ?  \n[y/n] ')
        if create.lower() in ["y", "yes"]:
            print(f'Creating location: {path}')
            os.makedirs(path)
        print(f'Creating {path}')

    def update_dockercompose(self, service: str):
        dockercompose_root = """version: '3.7'\nservices:"""
        if not self.dockercompose:
            self.dockercompose = dockercompose_root
        try:
            self.dockercompose += COMPOSE[service](self.title)
            service_root = Path(self.root_dir, service)
            os.chdir(service_root)
            with open("Dockerfile", "w") as dockerfile:
                dockerfile.write(DOCKERFILE[service])

        except Exception as e:
            print(e)

    def write_dockercompose(self):
        print("Writing docker-compose.yml")
        os.chdir(self.root_dir)
        with open("docker-compose.yml", "w") as dockercompose:
            dockercompose.write(self.dockercompose)

    def create_react_app(self):
        # Creates a react typescript skeleton
        path = self.root_dir
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
            command = ["yarn", "create", "react-app", "app"]
            if "typescript" in self.options.keys():
                command = [*command, "--template", "typescript"]
            cra = subprocess.Popen(command)
            cra_output, cra_error = cra.communicate()
            if cra_error:
                print(cra_error)
                raise SystemError
            print(cra_output)

        def create_project_folders():
            print("\nCreating React Folders:\n")
            src = Path("app", "src")
            os.chdir(src)
            base = "ts"
            if "typescript" not in self.options.keys():
                base = "js"
            folders = [
                Path(base, "components"),
                Path(base, "types"),
                Path("assets", "css"),
                Path("assets", "img"),
                "data",
            ]
            for folder in folders:
                print(folder)
                os.makedirs(folder)

        def yarn_deps():
            print("\nInstalling Dependencies")
            deps = subprocess.Popen(
                ["yarn", "add", "node-sass", "jotai"]
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

        yarn_install()
        yarn_cra()
        yarn_deps()
        self.update_dockercompose("app")

    def create_project(self):
        options = self.options.keys()
        try:
            if not self.title:
                # set random title if not provided
                self.set_title()
            if not os.path.isdir(self.location):
                # create path for project root
                self.create_directory(self.location)
            if "react-app" in options:
                try:
                    self.create_react_app()
                except SystemError:
                    print("ERROR: creating react app")
                    return
            if "dockerize" in options:
                self.write_dockercompose()

            exit

        except KeyboardInterrupt:
            print("\nAdios!\n")


def get_args() -> dict:
    help = """HELP:
    [r] - create-react-app
    [t] - Typescript when combined with -r
    [d] - Dockerize - create docker-compose file for services created by project
    [f] - Create a flask api
    [n] - Name: project name - defaults to random two(2) words
    [l] - Location: project location
    """
    payload = {"options": {}}
    argument_list = sys.argv[1:]
    opts = "rtdn:l:h"
    try:
        arguments, values = getopt.getopt(argument_list, opts)

        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h"):
                print(help)
                return {"help": True}

            elif currentArgument in ("-r"):
                payload["options"]["react-app"] = True

            elif currentArgument in ("-t"):
                payload["options"]["typescript"] = True

            elif currentArgument in ("-f"):
                payload["options"]["flask"] = True

            elif currentArgument in ("-d"):
                payload["options"]["dockerize"] = True

            elif currentArgument in ("-n"):
                payload["title"] = currentValue

            elif currentArgument in ("-l"):
                payload["location"] = currentValue

    except getopt.error as err:
        print(str(err))

    return payload


if __name__ == "__main__":
    creatables = ["react-app", "flask"]

    args = get_args()
    is_creating = False
    for k in args["options"].keys():
        if k in creatables:
            is_creating = True
            break
    if is_creating:
        p = Project(**args).create_project()
    elif "help" not in args.keys():
        print("No project type selected.\nUse -h for HELP.")
