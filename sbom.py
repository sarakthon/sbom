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

    print(f"Saved SBOM in CSV format to {output_file}")

    return output_file


def write_to_json(directory_path: Path, dependencies):
    output_file = directory_path / "sbom.json"

    json_data = []

    for name, version, pkg, path in dependencies:
        json_data.append({
                        "name": name,
                        "version": version,
                        "type": pkg,
                        "path": str(path)
                        })
        
    with open(output_file, "w") as f:
        json.dump(json_data, f, indent=4)

    print(f"Saved SBOM in json format to {output_file}")


def main():
    directory_path = Path(sys.argv[1])

    repo_counter = 0
    dependencies = []

    for repo in directory_path.iterdir():
        if repo.is_dir():
            repo_counter += 1
            txt = repo / "requirements.txt"
            json = repo / "package.json"

            if txt.exists():
                txt_deps = read_txt(txt)
                pkg = "pip"
                for name, version in txt_deps:
                    dependencies.append((name, version, pkg, repo))
            
            if json.exists():
                json_deps =read_json(json)
                pkg = "npm"
                for name, version in json_deps:
                    dependencies.append((name, version, pkg, repo))
   
    print(f"Found {repo_counter} repositories in {directory_path}")
    write_to_csv(directory_path, dependencies)
    write_to_json(directory_path, dependencies)

if __name__ == "__main__":
    main()