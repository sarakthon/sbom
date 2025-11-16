import sys
from pathlib import Path


def main():
    directory_path = Path(sys.argv[1])
    for repo in directory_path.iterdir():
        if repo.is_dir():
            txt = repo / "requirements.txt"
            json = repo / "package.json"

            if txt.exists():
                print(".txt exists")
            
            if json.exists():
                print(".json exists")


if __name__ == "__main__":
    main()