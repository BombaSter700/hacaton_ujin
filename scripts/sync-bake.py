"""Generate the JSON Bake equivalent from HCL. Use --check in CI."""

import argparse
import json
import os
import re
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
HCL = "infra/docker/docker-bake.hcl"
JSON = ROOT / "infra/docker/docker-bake.json"
# This HCL deliberately uses string defaults; fail if that contract changes.
DEFAULTS = {
    name: json.loads(value)
    for name, value in re.findall(
        r'variable\s+"([^" ]+)"\s*\{\s*default\s*=\s*("[^"\n]*")\s*\}',
        (ROOT / HCL).read_text(encoding="utf-8"),
    )
}
if set(DEFAULTS) != {"DOCKER_REGISTRY", "IMAGE_TAG", "TARGET_PLATFORM"}:
    raise SystemExit("Expected three string-default Bake variables")


def plan(file, values):
    env = {**os.environ, **values}
    env.pop("BUILDX_BAKE_FILE", None)
    result = subprocess.run(
        ["docker", "buildx", "bake", "-f", file, "--print"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    resolved = plan(HCL, DEFAULTS)
    generated = json.loads(json.dumps(resolved))
    generated["variable"] = {key: {"default": value} for key, value in DEFAULTS.items()}
    for name, target in generated["target"].items():
        path = ROOT / target["context"] / target["dockerfile"]
        if not path.is_file():
            raise SystemExit(f"Missing Dockerfile: {path}")
        target["tags"] = ["${DOCKER_REGISTRY}/" + name + ":${IMAGE_TAG}"]
        target["platforms"] = ["${TARGET_PLATFORM}"]
    content = json.dumps(generated, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if (
            not JSON.exists()
            or json.loads(JSON.read_text(encoding="utf-8")) != generated
        ):
            raise SystemExit("Bake JSON is stale; run python scripts/sync-bake.py")
    else:
        JSON.write_text(content, encoding="utf-8", newline="\n")
    for values in (
        DEFAULTS,
        {**DEFAULTS, "IMAGE_TAG": "sha-" + "a" * 40, "TARGET_PLATFORM": "linux/arm64"},
    ):
        if plan(HCL, values) != plan(str(JSON), values):
            raise SystemExit("HCL and JSON Bake plans differ")
    print("PASS: HCL and JSON agree for default and overridden variables")


if __name__ == "__main__":
    main()
