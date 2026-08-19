#!/usr/bin/env node
/**
 * Centralized version bump script for Tauri desktop app.
 *
 * Updates all version files to match the specified semver.
 * Run BEFORE creating a release tag.
 *
 * Usage: node scripts/bump-version.js <semver>
 * Example: node scripts/bump-version.js 1.2.0
 */

const fs = require("fs");
const path = require("path");

const version = process.argv[2];
if (!version) {
    console.error("Usage: node bump-version.js <semver>");
    process.exit(1);
}

// Validate semver format
if (!/^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$/.test(version)) {
    console.error(`Error: "${version}" is not a valid semver string`);
    process.exit(1);
}

const files = [
    { path: "frontend/package.json", type: "json" },
    { path: "desktop/frontend/package.json", type: "json" },
    { path: "desktop/frontend/package-lock.json", type: "json" },
    { path: "desktop/src-tauri/tauri.conf.json", type: "json" },
    { path: "desktop/src-tauri/Cargo.toml", type: "cargo" },
    { path: "backend/pyproject.toml", type: "pyproject" },
    { path: "desktop/frontend/src/app/startup/page.tsx", type: "ui" },
    { path: "desktop/frontend/messages/en.json", type: "i18n" },
    { path: "desktop/frontend/messages/it.json", type: "i18n" },
];

let updated = 0;
let errors = [];

for (const file of files) {
    const fullPath = path.resolve(file.path);
    if (!fs.existsSync(fullPath)) {
        errors.push(`  SKIP ${file.path} — file not found`);
        continue;
    }

    try {
        let content = fs.readFileSync(fullPath, "utf-8");

        switch (file.type) {
            case "json":
            case "i18n": {
                const data = JSON.parse(content);
                data.version = version;
                fs.writeFileSync(fullPath, JSON.stringify(data, null, 2) + "\n");
                break;
            }
            case "cargo": {
                content = content.replace(
                    /^version\s*=\s*"[^"]+"/m,
                    `version = "${version}"`
                );
                fs.writeFileSync(fullPath, content);
                break;
            }
            case "pyproject": {
                content = content.replace(
                    /^version\s*=\s*"[^"]+"/m,
                    `version = "${version}"`
                );
                fs.writeFileSync(fullPath, content);
                break;
            }
            case "ui": {
                // Update version string in UI components (e.g., "v0.1.0" → "v1.2.0")
                content = content.replace(
                    /v\d+\.\d+\.\d+/g,
                    `v${version}`
                );
                fs.writeFileSync(fullPath, content);
                break;
            }
        }
        console.log(`  ✓ ${file.path} → ${version}`);
        updated++;
    } catch (err) {
        errors.push(`  ERR ${file.path}: ${err.message}`);
    }
}

console.log(`\nUpdated ${updated}/${files.length} files to version ${version}`);
if (errors.length > 0) {
    console.log("\nErrors:");
    errors.forEach((e) => console.log(e));
}
