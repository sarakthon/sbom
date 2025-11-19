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

def read_package_lock(lock_path: Path):
    data = json.loads(lock_path.read_text())
    dependencies = []

    packages = data.get("packages", {})

    for package_path, package_info in packages.items():
        if package_path == "":
            continue
        
        if package_path.startswith("node_modules/"):
            package_name = package_path.split("node_modules/")[-1]
        else:
            package_name = package_path

        version = package_info.get("version")
        if version:
            dependencies.append((package_name, version, "npm"))
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
    if len(sys.argv) != 2:
        print("Missing arg PATH_TO_FOLDER\n\nUSAGE: python3 sbom.py PATH_TO_FOLDER")
        sys.exit(1)

    directory_path = Path(sys.argv[1])

    if not directory_path.exists():
        print(f"Error: Folder {directory_path} does not exist.")
        sys.exit(1)

    repo_counter = 0
    dependency_set = {}

    for repo in directory_path.iterdir():
        if repo.is_dir():
            repo_counter += 1
            txt = repo / "requirements.txt"
            json = repo / "package.json"
            json_lock = repo / "package-lock.json"

            if txt.exists():
                txt_deps = read_txt(txt)
                for name, version in txt_deps:
                    add_if_not_present(dependency_set, name, version, "pip", repo)
            
            if json_lock.exists():
                print("found lockfile")
                lock_deps = read_package_lock(json_lock)
                for name, version, pkg in lock_deps:
                    add_if_not_present(dependency_set, name, version, "npm", repo)
            elif json.exists():
                json_deps =read_json(json)
                for name, version in json_deps:
                    add_if_not_present(dependency_set, name, version, "npm", repo)

    dependencies = []
    for key in dependency_set:
        dep = dependency_set.get(key)
        dependencies.append(dep)

    print(f"Found {repo_counter} repositories in {directory_path}")
    write_to_csv(directory_path, dependencies)
    write_to_json(directory_path, dependencies)

def add_if_not_present(dependencies, name, version, package_system, repo):
    key = name+version+package_system
    if dependencies.get(key) != None:
        return # Already added
    else:
        dependencies[key] = (name, version, package_system, repo)

    return dependencies


if __name__ == "__main__":
    main()