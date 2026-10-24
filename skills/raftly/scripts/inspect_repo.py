#!/usr/bin/env python3
"""Inspect a repository and print structured JSON only (no prose, no network, no execution).

Detects languages, package managers, frameworks, build files, CI, containers, infrastructure,
databases/migrations, test frameworks, frontend/backend/mobile boundaries, Raftly state, and
suggests an operating mode. Never executes project code; only reads file names and manifests.

  inspect_repo.py [--root DIR] [--max-files 20000]
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgelib import yamlio  # noqa: E402

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build", ".next", ".nuxt", ".svelte-kit",
    "target", ".gradle", "Pods", ".expo", ".turbo", ".cache", "coverage", ".idea", ".vscode", "vendor", ".raftly", ".forge",
    "DerivedData", ".dart_tool", ".terraform", "out", ".output", ".parcel-cache", "bower_components",
}
LANG_EXT = {
    ".ts": "TypeScript", ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".py": "Python", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".java": "Java", ".kt": "Kotlin",
    ".swift": "Swift", ".m": "Objective-C", ".dart": "Dart", ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C",
    ".ex": "Elixir", ".exs": "Elixir", ".scala": "Scala", ".vue": "Vue", ".svelte": "Svelte", ".sql": "SQL",
    ".sh": "Shell", ".html": "HTML", ".css": "CSS", ".scss": "CSS",
}
DOC_EXT = {".md", ".txt", ".rst", ".adoc", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".svg"}

NPM_FRAMEWORKS = {
    "next": "Next.js", "react": "React", "react-dom": "React DOM", "vue": "Vue", "nuxt": "Nuxt", "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit", "astro": "Astro", "@remix-run/react": "Remix", "solid-js": "Solid", "@angular/core": "Angular",
    "vite": "Vite", "expo": "Expo", "react-native": "React Native", "react-native-web": "React Native Web",
    "express": "Express", "fastify": "Fastify", "@nestjs/core": "NestJS", "hono": "Hono", "koa": "Koa",
    "tailwindcss": "Tailwind CSS", "electron": "Electron", "@tauri-apps/api": "Tauri", "@capacitor/core": "Capacitor",
    "graphql": "GraphQL", "@trpc/server": "tRPC", "socket.io": "Socket.IO",
}
NPM_DATA = {
    "prisma": "Prisma", "@prisma/client": "Prisma", "drizzle-orm": "Drizzle", "typeorm": "TypeORM", "sequelize": "Sequelize",
    "mongoose": "MongoDB (Mongoose)", "mongodb": "MongoDB", "pg": "PostgreSQL", "postgres": "PostgreSQL", "mysql2": "MySQL",
    "better-sqlite3": "SQLite", "redis": "Redis", "ioredis": "Redis", "firebase": "Firebase", "firebase-admin": "Firebase",
    "@supabase/supabase-js": "Supabase", "knex": "Knex", "kysely": "Kysely", "@aws-sdk/client-dynamodb": "DynamoDB",
}
NPM_SERVICES = {
    "stripe": "Stripe", "@stripe/stripe-js": "Stripe", "openai": "OpenAI", "@anthropic-ai/sdk": "Anthropic",
    "@sentry/node": "Sentry", "@sentry/react": "Sentry", "@sentry/nextjs": "Sentry", "posthog-js": "PostHog",
    "next-auth": "Auth.js", "@auth/core": "Auth.js", "@clerk/nextjs": "Clerk", "resend": "Resend", "@sendgrid/mail": "SendGrid",
    "bullmq": "BullMQ", "@aws-sdk/client-s3": "AWS S3", "langchain": "LangChain", "ai": "Vercel AI SDK",
}
NPM_TESTS = {"jest": "Jest", "vitest": "Vitest", "@playwright/test": "Playwright", "cypress": "Cypress", "mocha": "Mocha",
             "@testing-library/react": "Testing Library", "detox": "Detox"}
PY_PKGS = {
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "sqlalchemy": "SQLAlchemy", "alembic": "Alembic",
    "pytest": "pytest", "celery": "Celery", "pydantic": "Pydantic", "psycopg": "PostgreSQL", "psycopg2": "PostgreSQL",
    "psycopg2-binary": "PostgreSQL", "pymongo": "MongoDB", "redis": "Redis", "openai": "OpenAI", "anthropic": "Anthropic",
    "stripe": "Stripe", "streamlit": "Streamlit", "langchain": "LangChain", "boto3": "AWS SDK",
}


def walk(root: Path, max_files: int):
    files = []
    truncated = False
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".") or d in (".github", ".circleci", ".gitlab"))
        for f in sorted(filenames):
            files.append(Path(dirpath) / f)
            if len(files) >= max_files:
                truncated = True
                return files, truncated
    return files, truncated


def read_json(p: Path) -> dict:
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def read_small(p: Path, limit: int = 200_000) -> str:
    try:
        if p.stat().st_size > limit:
            return ""
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def inspect(root: Path, max_files: int = 20000) -> dict:
    root = root.resolve()
    files, truncated = walk(root, max_files)
    rel = [f.relative_to(root).as_posix() for f in files]
    names = {Path(r).name for r in rel}
    langs = Counter(LANG_EXT[Path(r).suffix.lower()] for r in rel if Path(r).suffix.lower() in LANG_EXT)
    code_files = sum(langs.values())
    only_docs = bool(rel) and all(Path(r).suffix.lower() in DOC_EXT or Path(r).name in ("LICENSE", ".gitignore") for r in rel)

    out: dict = {
        "root": str(root), "file_count": len(rel), "truncated": truncated, "code_files": code_files,
        "is_empty": len(rel) == 0, "docs_only": only_docs,
        "languages": dict(langs.most_common()), "package_managers": [], "frameworks": [], "data": [], "services": [],
        "tests": [], "build_files": [], "ci": [], "containers": [], "infra": [], "migrations": [],
        "boundaries": {"frontend": [], "backend": [], "mobile": [], "packages": []},
        "env_files": [], "docs": {"readme": False, "license": False, "contributing": False},
        "state": {"present": False}, "signals": [],
    }

    # package.json files (root + workspaces, shallow)
    pkg_files = [root / r for r in rel if Path(r).name == "package.json" and r.count("/") <= 3]
    deps_all: dict[str, str] = {}
    for pf in pkg_files:
        data = read_json(pf)
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            deps_all.update(data.get(key) or {})
        if pf.parent != root:
            out["boundaries"]["packages"].append(pf.parent.relative_to(root).as_posix())
    if pkg_files:
        for lock, pm in (("pnpm-lock.yaml", "pnpm"), ("yarn.lock", "yarn"), ("bun.lockb", "bun"), ("bun.lock", "bun"),
                         ("package-lock.json", "npm")):
            if lock in names:
                out["package_managers"].append(pm)
        if not out["package_managers"]:
            out["package_managers"].append("npm (no lockfile)")
    for dep in deps_all:
        for table, key in ((NPM_FRAMEWORKS, "frameworks"), (NPM_DATA, "data"), (NPM_SERVICES, "services"), (NPM_TESTS, "tests")):
            if dep in table and table[dep] not in out[key]:
                out[key].append(table[dep])

    # python
    py_text = ""
    for fname in ("requirements.txt", "pyproject.toml", "Pipfile", "setup.py", "setup.cfg"):
        for r in rel:
            if Path(r).name == fname and r.count("/") <= 2:
                py_text += read_small(root / r).lower() + "\n"
                if fname == "pyproject.toml" and "poetry" in py_text:
                    out["package_managers"].append("poetry")
                elif fname == "Pipfile":
                    out["package_managers"].append("pipenv")
                elif "pip" not in out["package_managers"]:
                    out["package_managers"].append("pip")
    if "uv.lock" in names:
        out["package_managers"].append("uv")
    for pkg, label in PY_PKGS.items():
        if re.search(rf"(^|[\s\"'\[,]){re.escape(pkg)}([\s<>=~!\[;,\"']|$)", py_text, re.M):
            bucket = "tests" if label == "pytest" else ("data" if label in ("SQLAlchemy", "Alembic", "PostgreSQL", "MongoDB", "Redis") else
                                                         "services" if label in ("OpenAI", "Anthropic", "Stripe", "AWS SDK", "LangChain") else "frameworks")
            if label not in out[bucket]:
                out[bucket].append(label)

    simple = {
        "go.mod": ("Go modules", "package_managers"), "Cargo.toml": ("cargo", "package_managers"),
        "Gemfile": ("bundler", "package_managers"), "composer.json": ("composer", "package_managers"),
        "pubspec.yaml": ("Flutter/Dart pub", "package_managers"), "Podfile": ("CocoaPods", "package_managers"),
        "build.gradle": ("Gradle", "build_files"), "build.gradle.kts": ("Gradle", "build_files"), "pom.xml": ("Maven", "build_files"),
        "Makefile": ("Make", "build_files"), "CMakeLists.txt": ("CMake", "build_files"), "turbo.json": ("Turborepo", "build_files"),
        "nx.json": ("Nx", "build_files"), "Dockerfile": ("Dockerfile", "containers"), "docker-compose.yml": ("Docker Compose", "containers"),
        "docker-compose.yaml": ("Docker Compose", "containers"), "compose.yaml": ("Docker Compose", "containers"),
        "vercel.json": ("Vercel", "infra"), "netlify.toml": ("Netlify", "infra"), "fly.toml": ("Fly.io", "infra"),
        "render.yaml": ("Render", "infra"), "app.json": ("Expo/app config", "build_files"), "eas.json": ("EAS Build", "build_files"),
        "firebase.json": ("Firebase", "infra"), "serverless.yml": ("Serverless Framework", "infra"), "wrangler.toml": ("Cloudflare Workers", "infra"),
        "Procfile": ("Procfile (Heroku-style)", "infra"), "pytest.ini": ("pytest", "tests"), "jest.config.js": ("Jest", "tests"),
        "vitest.config.ts": ("Vitest", "tests"), "playwright.config.ts": ("Playwright", "tests"), "cypress.config.ts": ("Cypress", "tests"),
        "manage.py": ("Django", "frameworks"), "Gemfile.lock": ("Ruby", "build_files"),
    }
    for fname, (label, bucket) in simple.items():
        if fname in names and label not in out[bucket]:
            out[bucket].append(label)
    if "Gemfile" in names and "rails" in read_small(root / "Gemfile").lower():
        out["frameworks"].append("Rails")
    if "go.mod" in names:
        gm = read_small(root / "go.mod")
        for mod, label in (("gin-gonic", "Gin"), ("labstack/echo", "Echo"), ("go-chi", "chi"), ("gorm.io", "GORM")):
            if mod in gm:
                out["frameworks"].append(label)

    for r in rel:
        if r.startswith(".github/workflows/") and r.endswith((".yml", ".yaml")):
            out["ci"].append(r)
        elif r in (".gitlab-ci.yml", "Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml") or r.startswith(".circleci/"):
            out["ci"].append(r)
        if r.endswith(".tf") and "Terraform" not in out["infra"]:
            out["infra"].append("Terraform")
        if re.search(r"(^|/)(k8s|kubernetes|helm|charts)/", r) and "Kubernetes" not in out["infra"]:
            out["infra"].append("Kubernetes")
        if re.search(r"(^|/)(migrations|migrate|alembic|prisma/migrations|db/migrate|supabase/migrations)(/|$)", r):
            d = re.match(r"(.*?(migrations|migrate|alembic))(/|$)", r)
            m = d.group(1) if d else r
            if m not in out["migrations"]:
                out["migrations"].append(m)
        if Path(r).name.startswith(".env") and Path(r).name not in out["env_files"]:
            out["env_files"].append(Path(r).name)
        if r.endswith("schema.prisma") and "Prisma" not in out["data"]:
            out["data"].append("Prisma")
    out["migrations"] = out["migrations"][:20]

    top = sorted({r.split("/")[0] for r in rel if "/" in r})
    for d in top:
        low = d.lower()
        if low in ("web", "frontend", "client", "app", "apps", "ui", "site", "www", "pages", "src"):
            out["boundaries"]["frontend"].append(d)
        if low in ("api", "server", "backend", "services", "functions", "worker", "workers"):
            out["boundaries"]["backend"].append(d)
        if low in ("mobile", "ios", "android", "native"):
            out["boundaries"]["mobile"].append(d)

    out["docs"] = {"readme": any(n.lower().startswith("readme") for n in names),
                   "license": any(n.upper().startswith(("LICENSE", "LICENCE")) for n in names),
                   "contributing": any(n.upper().startswith("CONTRIBUTING") for n in names)}

    from forgelib.project import FORGE_DIR, LEGACY_DIRS

    state_path = next((root / d / "state.yaml" for d in [FORGE_DIR, *LEGACY_DIRS] if (root / d / "state.yaml").exists()),
                      root / FORGE_DIR / "state.yaml")
    if state_path.exists():
        try:
            st = yamlio.load_file(state_path) or {}
            meta = st.get("engine") or st.get("forge") or {}
            out["state"] = {"present": True, "valid_yaml": True, "dir": state_path.parent.name, "mode": st.get("project", {}).get("mode"),
                            "stage": st.get("project", {}).get("stage"),
                            "schema_version": meta.get("schema_version")}
        except yamlio.YAMLError as exc:
            out["state"] = {"present": True, "valid_yaml": False, "error": str(exc)}

    # signals and suggested mode
    sig = out["signals"]
    if out["env_files"] and ".env" in out["env_files"]:
        sig.append("a .env file exists in the tree: verify it is gitignored and contains no committed secrets")
    if code_files and not out["tests"]:
        sig.append("no test framework detected")
    if code_files and not out["ci"]:
        sig.append("no CI configuration detected")
    if out["data"] and not out["migrations"] and any(x in out["data"] for x in ("PostgreSQL", "MySQL", "Prisma", "Drizzle", "SQLAlchemy", "TypeORM")):
        sig.append("relational database client detected without a migrations directory")
    if "Firebase" in out["data"] or "Firebase" in out["infra"]:
        sig.append("Firebase in use")
    if out["state"].get("present"):
        mode = "BUILD"
    elif out["is_empty"] or out["docs_only"] or code_files == 0:
        mode = "GREENFIELD"
    else:
        mode = "REVIEW"  # Raftly Director refines to RECOVERY/MIGRATION/LAUNCH/DOCTOR from the user's goal
    out["suggested_mode"] = mode
    return out


def main(argv: list[str]) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="inspect_repo.py", description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--max-files", type=int, default=20000)
    args = p.parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(json.dumps({"error": f"not a directory: {root}"}))
        return 2
    print(json.dumps(inspect(root, args.max_files), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
