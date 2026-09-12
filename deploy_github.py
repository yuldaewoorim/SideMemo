import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_NAME = "yuldaewoorim/SideMemo"
SIDEMEMO_PY = BASE_DIR / "sidememo.py"
ISS_FILE = BASE_DIR / "SideMemo.iss"
VERSION_JSON = BASE_DIR / "version.json"
INSTALLER_EXE = BASE_DIR / "installer" / "SideMemo-Setup.exe"


def get_current_version() -> str:
    content = SIDEMEMO_PY.read_text(encoding="utf-8")
    m = re.search(r'APP_VERSION\s*=\s*["\']([^"\']+)["\']', content)
    if m:
        return m.group(1)
    if VERSION_JSON.exists():
        try:
            data = json.loads(VERSION_JSON.read_text(encoding="utf-8"))
            return data.get("version", "1.0.0")
        except Exception:
            pass
    return "1.0.0"


def bump_version_str(ver: str, bump_type: str = "patch") -> str:
    nums = [int(x) for x in re.findall(r'\d+', ver)]
    while len(nums) < 3:
        nums.append(0)
    major, minor, patch = nums[0], nums[1], nums[2]
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_version_files(new_ver: str):
    print(f"Updating files with version: v{new_ver}...")
    # 1. sidememo.py
    py_text = SIDEMEMO_PY.read_text(encoding="utf-8")
    py_text = re.sub(r'APP_VERSION\s*=\s*["\'][^"\']+["\']', f'APP_VERSION = "{new_ver}"', py_text)
    SIDEMEMO_PY.write_text(py_text, encoding="utf-8")

    # 2. SideMemo.iss
    if ISS_FILE.exists():
        iss_text = ISS_FILE.read_text(encoding="utf-8")
        iss_text = re.sub(r'AppVersion\s*=\s*[^\r\n]+', f'AppVersion={new_ver}', iss_text)
        ISS_FILE.write_text(iss_text, encoding="utf-8")

    # 3. version.json
    v_data = {
        "version": new_ver,
        "repository": REPO_NAME,
        "updated_at": datetime.date.today().isoformat()
    }
    VERSION_JSON.write_text(json.dumps(v_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Version updated to v{new_ver} in sidememo.py, SideMemo.iss, version.json.")


def run_cmd(cmd, cwd=None):
    print(f"Executing: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd or str(BASE_DIR), capture_output=True, text=True, shell=isinstance(cmd, str))
    if res.returncode != 0:
        print(f"Error (code {res.returncode}):")
        if res.stdout:
            print("STDOUT:", res.stdout[-800:])
        if res.stderr:
            print("STDERR:", res.stderr[-800:])
    return res


def build_binaries():
    print("Building fresh installer via build_release.py...")
    build_script = BASE_DIR / "build_release.py"
    res = run_cmd([sys.executable, str(build_script)])
    if res.returncode != 0 or not INSTALLER_EXE.exists():
        print("Build failed! Check errors above.")
        return False
    size_mb = INSTALLER_EXE.stat().st_size / (1024 * 1024)
    print(f"Installer built successfully: {INSTALLER_EXE} ({size_mb:.2f} MB)")
    return True


def git_deploy(new_ver: str, release_notes: str = ""):
    tag_name = f"v{new_ver}"
    print(f"Preparing Git commit and tag for {tag_name}...")

    # Init git if needed
    if not (BASE_DIR / ".git").exists():
        run_cmd(["git", "init", "-b", "main"])

    # Configure user if not set
    run_cmd(["git", "config", "user.name", "yuldaewoorim"])
    run_cmd(["git", "config", "user.email", "ulimi072@gmail.com"])

    # Ensure remote origin
    remotes = run_cmd(["git", "remote", "-v"]).stdout
    remote_url = f"https://github.com/{REPO_NAME}.git"
    if "origin" not in remotes:
        run_cmd(["git", "remote", "add", "origin", remote_url])
    else:
        run_cmd(["git", "remote", "set-url", "origin", remote_url])

    # Git add and commit
    run_cmd(["git", "add", "."])
    commit_msg = f"Release {tag_name}"
    if release_notes:
        commit_msg += f"\n\n{release_notes}"
    run_cmd(["git", "commit", "-m", commit_msg])

    # Git tag
    run_cmd(["git", "tag", "-a", tag_name, "-m", f"SideMemo {tag_name}", "-f"])

    print(f"Pushing to GitHub ({remote_url})...")
    push_res = run_cmd(["git", "push", "-u", "origin", "main", "--tags"])
    if push_res.returncode == 0:
        print(f"Successfully pushed commits and tag {tag_name} to GitHub!")
        return True
    else:
        print("Git push completed with status:", push_res.returncode)
        return False


def main():
    parser = argparse.ArgumentParser(description="SideMemo GitHub Auto Release & Deployment")
    parser.add_argument("--bump", choices=["patch", "minor", "major"], default="patch",
                        help="Version bump type (default: patch)")
    parser.add_argument("--version", type=str, default="",
                        help="Explicit version (e.g. 1.0.1)")
    parser.add_argument("--notes", type=str, default="",
                        help="Release notes text")
    parser.add_argument("--skip-build", action="store_true",
                        help="Skip re-compiling binaries (use existing installer)")
    args = parser.parse_args()

    curr_ver = get_current_version()
    print(f"Current SideMemo version: v{curr_ver}")

    if args.version:
        new_ver = args.version.lstrip("vV")
    else:
        new_ver = bump_version_str(curr_ver, args.bump)

    print(f"Target deployment version: v{new_ver}")

    # 1. Update version in source files
    update_version_files(new_ver)

    # 2. Build binaries
    if not args.skip_build:
        if not build_binaries():
            print("Deployment aborted due to build failure.")
            sys.exit(1)

    # 3. Git commit, tag, and push
    git_deploy(new_ver, args.notes)

    print("\n" + "=" * 60)
    print(f"SideMemo v{new_ver} Deployment Process Finished!")
    print(f"Repository: https://github.com/{REPO_NAME}")
    print(f"Releases URL: https://github.com/{REPO_NAME}/releases")
    print(f"Installer: {INSTALLER_EXE}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

