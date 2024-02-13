import json
import subprocess

r = {}
with open("/home/evaldas/projects/ceasium/ceasium/packages.json") as f:
    j = json.loads(f.read())
    for package in j:
        a = j[package]["apt"]
        o = subprocess.run(
            f"apt search {a}",
            shell=True,
            capture_output=True,
            text=True
        )
        if not o.stdout.endswith("orting...\nFull Text Search...\n"):
            r[package] = {
                "apt": j[package]["apt"]
            }
with open("/home/evaldas/projects/ceasium/ceasium/packages.json", "w") as f:
    f.write(json.dumps(r, indent=4))
