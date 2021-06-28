#!/usr/bin/python3.9

from genericpath import exists
from utils import is_tool
from config import NODE_TOOL, PROJECT_ROOT
from docker.services import COMPOSE, DOCKERFILE
import os
import sys
import getopt
import random
import subprocess
import fileinput
from pathlib import Path
from fastapi.create_fast_api import build_fastapi_structure


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
        - eg. `torturous-flamingo`
        ** Requires input to accept title as randomized 
            titles can frequently be *ahem* innappropriate...
    create_directory(dir: str)
        create `dir` if not exists;
    update_dockercompose(service: str)
        Updates docker compose data to contain service;
    write_dockercompose()
        Writes `docker-compose.yml` to disk;
    create_react_app()
        Creates a react app via `create-react-app`;
        -t Indicates project to created with typescript tempplate
    create_project()
        create project skeleton within location;
    '''

    def __init__(self, title: str = None, location: str = None, options: dict = {}) -> None:
        self.title = title
        self.location = location or PROJECT_ROOT
        self.options = options
        self.dockercompose = None
        self.root_dir = Path(self.location, self.title)

        self.errors = ""

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
        else:
            message = f'{path} already exists.\n\n \
            --> Change project name (-n) or location (-l).\n\nSee HELP -h for more.'
            raise SystemError(message)
        os.chdir(path)  # Change to project root

        node_tool_commands = {
            "yarn": {
                "invoke": "yarn",
                "add": "add",
            },
            "npm": {
                "invoke": "npm",
                "add": "install"
            }
        }
        node_command = node_tool_commands[NODE_TOOL]

        def node_install():
            # install package.json
            node = subprocess.Popen(
                [node_command["invoke"], "install"])
            node_output, node_error = node.communicate()
            if node_error:
                print(node_error)
                raise SystemError
            print(node_output)

        def node_cra():
            # create-react-app typescript app
            print("\nCreating React App\n")
            command = [node_command["invoke"], "create", "react-app", "app"]
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

        def node_deps():
            print("\nInstalling Node Dependencies\n")
            deps = subprocess.Popen(
                [node_command["invoke"],
                    node_command["add"], "node-sass", "jotai"]
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
        if is_tool(NODE_TOOL):
            node_install()
            node_cra()
            node_deps()
            self.update_dockercompose("app")
        else:
            print(f'ERROR: \'{NODE_TOOL}\' not installed')

    def create_fast_api(self) -> None:
        build_fastapi_structure(self.root_dir)

    def create_project(self):
        options = self.options.keys()
        try:
            if not self.title:
                # set random title if not provided
                self.set_title()
            if not os.path.isdir(self.location):
                # create path for project
                self.create_directory(self.location)
            if not os.path.isdir(self.root_dir):
                # create path for project root
                self.create_directory(self.root_dir)
            if "react-app" in options:
                try:
                    self.create_react_app()
                except SystemError as e:
                    print("ERROR: creating react app")
                    print(e)
                    return
            if "fastapi" in options:
                try:
                    self.create_fast_api()
                except Exception as e:
                    print(e)
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
    [f] - Create a FastAPI
    [n] - Name: project name - defaults to random two(2) words
    [l] - Location: project location
    """
    payload = {"options": {}}
    argument_list = sys.argv[1:]
    opts = "rtfdn:l:h"
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
                payload["options"]["fastapi"] = True

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
    creatables = ["react-app", "fastapi"]

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
