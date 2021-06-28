"""Create a FastAPI api
"""
import os

TITLE = ""

requirements_txt = "fastapi==0.63.0\nuvicorn==0.13.4"
main_py = """from fastapi import FastAPI

app = FastAPI(title="{0} FastAPI")


@app.get("/")
def read_root():
    return {1}"""


def build_fastapi_structure(proj_location: str) -> None:
    TITLE = str(proj_location).split("/")[-1]
    api = "api"

    os.chdir(proj_location)
    print("\nCreating api directory\n")
    os.mkdir(api)
    with open("requirements.txt", "w") as reqs:
        print("\nWriting 'requirements.txt'\n")
        reqs.write(requirements_txt)
    os.chdir(api)
    with open("main.py", "w") as file:
        print("\nWriting 'api/main.py'\n")
        file.write(main_py.format(TITLE, '{"hello": "world"}'))
    print(TITLE)
