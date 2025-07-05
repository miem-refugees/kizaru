import os
import re

import dotenv


def main():
    dotenv.load_dotenv()

    current_dir = os.path.dirname(os.path.abspath(__file__))

    folders = []
    for entry in os.listdir(current_dir):
        full_path = os.path.join(current_dir, entry)
        if os.path.isdir(full_path) and re.match(r"0[0-9]_", entry):
            if entry.startswith("00_"):
                continue

            folders.append(entry)

    folders.sort()
    print("Found stages:", folders)

    for stage in folders:
        stage_main = os.path.join(current_dir, stage, "main.py")

        if os.path.exists(stage_main):
            print(f"Running {stage}/main.py ...")
            os.system(f'python "{stage_main}"')
        else:
            print(f"No main.py found in {stage}, skipping.")


if __name__ == "__main__":
    main()
