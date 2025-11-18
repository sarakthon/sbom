import csv
import json
import sys
from pathlib import Path

# Function for parsing .txt-file
def read_txt(txt_path: Path):
    dependencies = []

    # Iterates through .txt-file and adds dependencies to list with their name and version
    with open(txt_path) as f:
        for line in f:
            line = line.strip()
            if "==" in line:
                name, version = line.split("==")
                dependencies.append((name, version))
    
    return dependencies

# Function for parsing json-file
def read_json(json_path: Path):
    dependencies = []

    with open(json_path) as f:
        data = json.load(f)

    # Parse dependencies and DevDependencies from package.json
    deps = data.get("dependencies", {})
    devDeps = data.get("DevDependencies", {})
    allDeps = deps | devDeps

    for name, version in allDeps.items():
        dependencies.append((name, version))
    
    return dependencies

def write_to_csv(directory_path: Path, dependencies):
    output_file = directory_path / "sbom.csv"

    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "version", "type", "absolute path"])
        writer.writerows(dependencies)


def write_to_json():
    ...

def main():
    directory_path = Path(sys.argv[1])

    repo_counter = 0
    dependencies = []

    for repo in directory_path.iterdir():
        repo_counter += 1
        
        if repo.is_dir():
            txt = repo / "requirements.txt"
            json = repo / "package.json"

            if txt.exists():
                txt_deps = read_txt(txt)
                for name, version in txt_deps:
                    dependencies.append((name, version, "npm", repo))
            
            if json.exists():
                json_deps =read_json(json)
                for name, version in json_deps:
                    dependencies.append((name, version, "pip", repo))

    print(f"Found {repo_counter} repositories in {directory_path}")
    
    csv = write_to_csv(directory_path, dependencies)

if __name__ == "__main__":
    main()