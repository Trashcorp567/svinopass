from pathlib import Path

env_path = Path("/opt/svinopass/.env")
patch = dict(
    line.split("=", 1)
    for line in Path("/tmp/postbox.env.patch").read_text().splitlines()
    if "=" in line
)
lines = env_path.read_text().splitlines()
out: list[str] = []
seen: set[str] = set()
for line in lines:
    key = line.split("=", 1)[0] if "=" in line else None
    if key in patch:
        out.append(f"{key}={patch[key]}")
        seen.add(key)
    else:
        out.append(line)
for key, value in patch.items():
    if key not in seen:
        out.append(f"{key}={value}")
env_path.write_text("\n".join(out) + "\n")
