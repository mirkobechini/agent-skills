---
name: tauri-v2-desktop-builder
version: 2.1.0
author: Mirko Bechini
description: "Build and release Tauri v2 desktop apps with Next.js static export + FastAPI PyInstaller sidecar. Covers project setup, tauri.conf.json, Rust commands, sidecar lifecycle, preflight checks, release CI, multi-OS builds, single-instance, startup UX, build optimization. Includes ALL known errors and solutions from 30+ release attempts across Windows/macOS/Linux."
argument-hint: "cargo tauri build | npm --prefix ../frontend exec tauri build"
user-invocable: true
applyTo: "**/desktop/**"
---

# Tauri v2 Desktop App Builder

## When to Use

Activate this skill when the user:

- Wants to create a new Tauri v2 desktop app from scratch
- Asks to build, fix, or debug a Tauri desktop app build/release process
- Needs to create or update the GitHub release workflow (release.yml)
- Has issues with sidecar (PyInstaller), NSIS installer, or macOS/Windows/Linux builds
- Wants to add Tauri commands or plugins (dialog, store, shell, updater, tray)
- Requests a preflight check before tagging a release

## Output

This skill produces:

1. **Tauri desktop app** — Compiled native binary (.msi/.dmg/.AppImage/.deb) for Windows, macOS, and Linux
2. **PyInstaller sidecar** — Single-file executable for the FastAPI backend, bundled inside the app
3. **GitHub Release** — Auto-generated draft release with platform-specific artifacts
4. **Preflight report** — Validation of all version files, dependencies, and builds before tagging

## Examples

### Example 1: First-time project setup

**User**: "Create a new Tauri desktop app for my project"

→ Follow Steps 1–8 in Procedure, then run `bash desktop/preflight.sh` to verify everything works.

### Example 2: Release a new version

**User**: "Release version 1.2.0"

→ Run `node scripts/bump-version.js 1.2.0`, verify with `bash desktop/preflight.sh`, then `git tag v1.2.0 && git push origin v1.2.0`.

### Example 3: Debug a failing macOS build

**User**: "The macOS build fails with 'sidecar binary not found'"

→ Check the error message against the Troubleshooting Flowchart. Likely fix: use `rustc -vV` for dynamic target triple detection instead of hardcoding.

> **Note on `desktop/frontend/` vs `frontend/`**: These are TWO separate Next.js projects. `frontend/` is the web version (deployed on Render/Vercel). `desktop/frontend/` is the desktop-specific version with Tauri integration code, different env vars, and `@tauri-apps/cli` as devDependency. They share components via a shared library or copy mechanism, but are independent builds.

```
project/
├── frontend/              ← Next.js static export (`output: 'export'`)
├── backend/               ← FastAPI (reused for sidecar)
├── desktop/               ← Tauri code
│   ├── src-tauri/         ← Rust (main, sidecar management, commands)
│   │   ├── binaries/      ← PyInstaller-built sidecar binary
│   │   ├── src/lib.rs
│   │   ├── src/main.rs
│   │   ├── build.rs       ← REQUIRED by tauri::generate_context!()
│   │   ├── Cargo.toml
│   │   ├── tauri.conf.json
│   │   └── capabilities/
│   ├── frontend/          ← Desktop-specific Next.js frontend (separate from web frontend)
│   │   ├── package.json   ← @tauri-apps/cli is a devDependency HERE
│   │   ├── node_modules/.bin/tauri  ← THE BINARY LIVES HERE
│   │   └── ...
│   ├── run_backend.py     ← PyInstaller entry point
│   ├── build-sidecar.ps1  ← Windows build script
│   ├── build-sidecar.sh   ← macOS/Linux build script
│   ├── preflight.sh       ← Cross-platform preflight check
│   ├── preflight.ps1      ← Windows preflight check
│   └── .env.desktop       ← Default env for desktop mode
```

## CRITICAL: Understanding Tauri CLI Binary Resolution

This is the #1 cause of release failures. **The Tauri CLI binary and the tauri.conf.json must be in specific directories.**

### Where things live

```
desktop/
├── frontend/                  ← CWD for npm run tauri (has node_modules/.bin/tauri)
│   ├── package.json           ← has "tauri": "tauri" script
│   ├── node_modules/
│   │   └── .bin/tauri         ← THE BINARY (symlink on macOS/Linux, .cmd on Windows)
│   └── ...
├── src-tauri/                 ← CWD for tauri build (has tauri.conf.json)
│   ├── tauri.conf.json        ← Tauri project config
│   ├── Cargo.toml
│   └── ...
```

### The Problem

- `npx` from `desktop/src-tauri/` looks for `node_modules/.bin/tauri` by walking UP the directory tree
- `desktop/src-tauri/` → `desktop/` → `project root/` → NEVER finds `desktop/frontend/node_modules/`
- `npx tauri build` from `desktop/src-tauri/` → **FAILS** with `npm error could not determine executable to run`

### The Solution: npm --prefix

```bash
cd desktop/src-tauri
npm --prefix ../frontend exec tauri build -- --ci
```

- `npm --prefix ../frontend` tells npm to find binaries in `desktop/frontend/node_modules/`
- `exec tauri build` runs the `tauri` binary found there
- `-- --ci` passes `--ci` to `tauri build` (the `--` separates npm args from tauri args)
- CWD stays `desktop/src-tauri/` so tauri.conf.json is found and all relative paths resolve correctly

### Why NOT alternatives

| Approach                                                                               | Why it fails                                                                           |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `npx tauri build --ci` from `desktop/src-tauri/`                                       | npx can't find the binary (sibling directory)                                          |
| `cd desktop/frontend && npx tauri build -- --config ../src-tauri/tauri.conf.json --ci` | Tauri searches for tauri.conf.json in CWD during project resolution, not from --config |
| `../frontend/node_modules/.bin/tauri build --ci` from `desktop/src-tauri/`             | Works on macOS/Linux but NOT on Windows (.cmd extension not found by bash)             |
| `cd desktop/frontend && npm run tauri build -- --ci`                                   | Tauri searches for tauri.conf.json in CWD but it's in src-tauri/                       |

## Prerequisites

### Required

- **Node.js** v22+ — For Next.js frontend
- **Python** 3.12+ — For FastAPI backend + PyInstaller
- **Rust** stable — For Tauri CLI and crate compilation
- **GitHub CLI** (gh) — For release workflow

### Platform-specific

**macOS**: Xcode CLI tools (`xcode-select --install`)
**Ubuntu/Debian**:

```bash
sudo apt-get install -y libwebkit2gtk-4.1-dev build-essential curl wget file \
  libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev
```

**Windows**: Microsoft C++ Build Tools (Desktop development with C++ workload)

## Procedure

### Step 1: Project structure

```bash
mkdir -p desktop/src-tauri/binaries desktop/src-tauri/src desktop/src-tauri/capabilities desktop/src-tauri/icons
```

Then create `desktop/src-tauri/build.rs`:

```rust
fn main() {
    tauri_build::build()
}
```

This file is **required** by `tauri::generate_context!()` — without it, `cargo build` fails with `OUT_DIR env var is not set`.

**Icons**: Tauri requires at least one icon file. On Windows, `icons/icon.ico` is needed for the resource file. Generate icons with:

```bash
# Option A: Use cargo tauri icon (if you have a 1024x1024 PNG)
cargo tauri icon path/to/icon.png

# Option B: Create minimal placeholders manually
# - icons/icon.ico (Windows)
# - icons/icon.png (macOS/Linux)
# - icons/32x32.png, icons/128x128.png, icons/128x128@2x.png (macOS)
# - icons/32x32.png, icons/128x128.png, icons/512x512.png (Linux)
```

### Step 2: Package.json with @tauri-apps/cli

```json
{
  "name": "desktop-frontend",
  "version": "0.1.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "tauri": "tauri"
  },
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "^2.11.4"
  }
}
```

**CRITICAL**: The `"tauri": "tauri"` script is required for `npm run tauri build` to work.

### Step 3: Cargo.toml dependencies

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon"] }  # tray-icon only if system tray needed
tauri-plugin-opener = "2"
tauri-plugin-shell = "2"
tauri-plugin-store = "2"
tauri-plugin-updater = "2"
tauri-plugin-dialog = "2"   # File picker dialogs (open/save)
tauri-plugin-single-instance = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
log = "0.4"

[build-dependencies]
tauri-build = { version = "2", features = [] }

[target.'cfg(not(target_os = "windows"))'.dependencies]
nix = { version = "0.29", features = ["signal"] }
```

### Step 4: tauri.conf.json

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "App Name",
  "version": "0.1.0",
  "identifier": "com.example.app",
  "build": {
    "beforeDevCommand": {
      "script": "npm run dev",
      "cwd": "../frontend"
    },
    "devUrl": "http://localhost:3000",
    "beforeBuildCommand": {
      "script": "npm run build",
      "cwd": "../frontend"
    },
    "frontendDist": "../frontend/out"
  },
  "bundle": {
    "active": true,
    "targets": "all",
    "icon": ["icons/icon.png"],
    "externalBin": ["binaries/fastapi-sidecar"],
    "windows": {
      "nsis": {
        "installMode": "currentUser",
        "installerHooks": "installer.nsh"
      }
    },
    "macOS": {
      "minimumSystemVersion": "10.15"
    }
  },
  "plugins": {
    "updater": {
      "endpoints": [
        "https://github.com/{owner}/{repo}/releases/latest/download/latest.json"
      ]
    }
  }
}
```

> **`installer.nsh`**: An NSIS header file that runs during install/uninstall. Used here to kill any running instance of the app before upgrade (prevents "Error" dialog during reinstall). Place it at `desktop/src-tauri/installer.nsh`. Minimal example:
>
> ```nsis
> !macro customInstall
>   nsExec::ExecToStack 'taskkill /F /IM "${PRODUCT_NAME}.exe" 2>NUL'
> !macroend
> ```

**Path resolution rules** (from Tauri source code):

- `beforeBuildCommand.cwd` is resolved relative to the process CWD (set to `dirs.tauri` = `desktop/src-tauri/`)
- `frontendDist` is resolved relative to the tauri.conf.json parent directory (`desktop/src-tauri/`)
- So `cwd: "../frontend"` resolves to `desktop/frontend/` and `frontendDist: "../frontend/out"` resolves to `desktop/frontend/out`

### Step 5: Capabilities (default.json)

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Capability for the main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "opener:default",
    "shell:allow-spawn",
    "shell:allow-execute",
    "shell:default",
    "store:default",
    "updater:default",
    "updater:allow-check",
    "updater:allow-download-and-install",
    "dialog:default",
    "dialog:allow-open"
  ]
}
```

### Step 6: Rust lib.rs and main.rs

Create `desktop/src-tauri/src/lib.rs` with the application logic:

```rust
use std::sync::Mutex;
use tauri::Manager;
use tauri_plugin_shell::ShellExt;

struct SidecarState {
    child: Mutex<Option<tauri_plugin_shell::process::CommandChild>>,
}

// Start sidecar (in setup closure)
fn start_sidecar(app: &tauri::App) {
    // Check if port 7723 is already responding (prevents duplicate sidecar)
    use std::net::TcpStream;
    let already_running = TcpStream::connect_timeout(
        &"127.0.0.1:7723".parse().unwrap(),
        std::time::Duration::from_millis(500),
    ).is_ok();
    if already_running {
        log::info!("Sidecar already running — skip spawn.");
        return;
    }

    let (mut rx, child) = app.shell()
        .sidecar("fastapi-sidecar")
        .unwrap()
        .spawn()
        .unwrap();

    // Read sidecar output in background async task (prevents buffer blocking)
    tauri::async_runtime::spawn(async move {
        use tauri_plugin_shell::process::CommandEvent;
        while let Some(event) = rx.recv().await {
            if let CommandEvent::Terminated(_) = event { break; }
        }
    });

    app.manage(SidecarState {
        child: Mutex::new(Some(child)),
    });
}

// Stop sidecar (on Destroyed)
fn stop_sidecar(app: &tauri::AppHandle) {
    if let Some(state) = app.try_state::<SidecarState>() {
        if let Some(child) = state.child.lock().unwrap().take() {
            let _ = child.kill();
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_updater::Builder::default().build())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            #[cfg(desktop)]
            {
                app.handle().plugin(
                    tauri_plugin_single_instance::init(|app, _args, _cwd| {
                        let _ = app
                            .get_webview_window("main")
                            .expect("no main window")
                            .set_focus();
                    }),
                ).expect("failed to register single-instance plugin");
            }

            start_sidecar(app);
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                stop_sidecar(window.app_handle());
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

Then create `desktop/src-tauri/src/main.rs` — the binary entry point:

```rust
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // Replace `app_name_lib` with your Cargo.toml package name (underscored)
    app_name_lib::run()
}
```

> **Note**: The crate name in `main.rs` must match your `Cargo.toml` `[package].name`, with hyphens replaced by underscores. For example, `name = "test-tauri-app"` → `test_tauri_app::run()`.

**Sidecar binary naming**: The binary must include the TARGET TRIPLE suffix:

- `fastapi-sidecar-x86_64-pc-windows-msvc.exe` (Windows)
- `fastapi-sidecar-aarch64-apple-darwin` (macOS ARM)
- `fastapi-sidecar-x86_64-apple-darwin` (macOS Intel)
- `fastapi-sidecar-x86_64-unknown-linux-gnu` (Linux)

**Always use `rustc -vV` to detect the host triple dynamically** — never hardcode it.

### Step 7: System tray (optional)

```rust
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::menu::{Menu, MenuItem};

// In .setup()
.tray(|app| {
    let show_item = MenuItem::with_id(app, "show", "Mostra", true, None::<&str>)?;
    let quit_item = MenuItem::with_id(app, "quit", "Esci", true, None::<&str>)?;
    let menu = Menu::with_items(app, &[&show_item, &quit_item])?;
    TrayIconBuilder::new()
        .icon(app.default_window_icon().unwrap().clone())
        .tooltip("App Name")
        .menu(&menu)
        .on_menu_event(move |app, event| { /* handle show/quit */ })
        .build()
})?;
```

### Step 8: PyInstaller sidecar

**Entry point** (`desktop/run_backend.py`):

```python
import os, sys, shutil

def _get_base_path():
    return sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(__file__)

def _ensure_env():
    base = _get_base_path()
    bundled = os.path.join(base, ".env.desktop")
    target = os.path.join(os.getcwd(), ".env")
    if not os.path.exists(target) and os.path.exists(bundled):
        shutil.copy2(bundled, target)

_ensure_env()

# Force imports for PyInstaller to trace
import app.main
import uvicorn

uvicorn.run("app.main:app", host="127.0.0.1", port=7723)
```

**Build script** (`desktop/build-sidecar.sh`):

```bash
pyinstaller --onefile --noconsole --name "fastapi-sidecar" \
  --paths "../backend" \
  --hidden-import "fitz" --collect-all "fitz" \
  --add-data ".env.desktop:." \
  --runtime-tmpdir "." \
  "run_backend.py"
```

> **Note on `--noconsole`**: Suppresses the terminal window on Windows (use for release builds). Remove `--noconsole` during development to see Python stdout/stderr.
>
> **Note on `--add-data` separator**: Use `:` on macOS/Linux (as shown) and `;` on Windows. The build script `build-sidecar.sh` is for macOS/Linux; use `build-sidecar.ps1` on Windows.

**CRITICAL**: `.env.desktop` must ONLY contain fields defined in the Settings model (pydantic_settings v2 with `extra='forbid'`). Remove `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `SIDECAR_PORT`, `STORAGE_LOCAL_PATH` if they're not model fields.

### Step 9: Release CI (.github/workflows/release.yml)

See `references/release.yml` for the complete working template. Key points:

- **Multi-job pipeline**: `wait-for-ci` → `build` (matrix: 3 OS) → `create-release`
- **Version bump**: Extracts version from git tag and updates all config files
- **Sidecar build**: PyInstaller → rename with target triple → place in `binaries/`
- **Tauri build**: Uses `npm --prefix ../frontend exec tauri build -- --ci` from `src-tauri/`
- **Artifacts**: Uploads .msi/.dmg/.AppImage/.deb per platform
- **Release**: Creates a draft release with `softprops/action-gh-release`

### Step 10: Preflight checklist (8 checks)

Create `desktop/preflight.sh` with these checks:

1. **npm ci** — frontend web
2. **npm ci** — desktop frontend
3. **next build** — desktop frontend static export
4. **pip install** — backend dependencies
5. **Sidecar imports** — simulate PyInstaller module loading
6. **Tauri CLI check** — `npm run tauri -- --version` from `desktop/frontend/`
7. **cargo check** — Rust compilation test from `desktop/src-tauri/`
8. **Version alignment** — all 9 version files must match

### Step 11: Version bump

Use the centralized script at `scripts/bump-version.js`:

```bash
node scripts/bump-version.js 1.2.0
```

The script updates all 9 version files: `frontend/package.json`, `desktop/frontend/package.json`, `desktop/frontend/package-lock.json`, `desktop/src-tauri/tauri.conf.json`, `desktop/src-tauri/Cargo.toml`, `backend/pyproject.toml`, startup UI component, and i18n message files (en/it).

See `scripts/bump-version.js` for the full implementation.

## Common Errors & Solutions

### 🔴 BLOCKING: npx can't find @tauri-apps/cli

```
npm error could not determine executable to run
```

**Cause**: `npx tauri build` from `desktop/src-tauri/` — `npx` walks up the tree looking for `node_modules/.bin/`, but the binary is in `desktop/frontend/node_modules/` (a sibling directory).

**Solution**: Use `npm --prefix ../frontend exec tauri build -- --ci` from `desktop/src-tauri/`.

### 🔴 BLOCKING: Tauri panics "Couldn't recognize the current folder as a Tauri project"

```
thread '<unnamed>' panicked at crates\tauri-cli\src\helpers\app_paths.rs:133:5:
Couldn't recognize the current folder as a Tauri project.
```

**Cause**: Running `tauri build` from a directory that doesn't contain `tauri.conf.json`.

**Solution**: `cd desktop/src-tauri` first, then run the build command.

### 🔴 BLOCKING: pydantic ValidationError on sidecar startup

```
pydantic_core.ValidationError: 3 validation errors for Settings
next_public_google_client_id → Extra inputs are not permitted
```

**Cause**: `.env.desktop` contains variables not defined in the Settings model (pydantic_settings v2 with `extra='forbid'`).

**Solution**: Remove `NEXT_PUBLIC_GOOGLE_CLIENT_ID`, `SIDECAR_PORT`, `STORAGE_LOCAL_PATH` from `.env.desktop`.

### 🔴 BLOCKING: npm ci fails — lock file desync

```
npm error Missing: @swc/helpers@0.5.23 from lock file
```

**Cause**: `package-lock.json` doesn't have the required `@swc/helpers` version.

**Solution**:

```bash
cd desktop/frontend
rm package-lock.json
npm install @swc/helpers@^0.5.23 --save-dev
rm -rf node_modules && npm ci
```

### 🔴 BLOCKING: Windows build fails — icon.ico not found or invalid

```
error RC2176 : old DIB in icons/icon.ico; pass it through SDKPAINT
```

or

```
`icons/icon.ico` not found; required for generating a Windows Resource file
```

**Cause**: Tauri on Windows requires a valid `icons/icon.ico` file for the resource compiler. On CI, icons are typically missing.

**Solution**: Use `cargo tauri icon path/to/icon.png` to generate all required icons. The source PNG should be at least 1024×1024. For a quick fix, download a placeholder or use the `tauri icon` CLI command.

### 🟡 WARNING: macOS build fails — sidecar binary not found

```
Error: sidecar binary not found: binaries/fastapi-sidecar-x86_64-apple-darwin
```

**Cause**: Hardcoded target triple in rename step, or missing `x86_64-apple-darwin` target.

**Solution**: Use `rustc -vV` dynamically. Install BOTH `aarch64-apple-darwin` AND `x86_64-apple-darwin`.

### 🟡 WARNING: PowerShell syntax error on Windows

```
ParserError: if [ ... ] is not a valid PowerShell expression
```

**Cause**: Using bash syntax in a step that runs on Windows.

**Solution**: Add `shell: bash` to all steps using bash syntax.

### 🟡 WARNING: cargo binstall fails on ARM macOS

```
HTTP 403: API rate limit exceeded
```

or

```
Binary not found for x86_64-apple-darwin on aarch64 runner
```

**Solution**: Use `@tauri-apps/cli` as npm devDependency instead of `cargo install`/`cargo binstall`.

### 🟡 WARNING: rust-cache not working

**Cause**: Wrong `workspaces` path.

**Solution**: Use `workspaces: "desktop/src-tauri -> target"` for nested projects.

### 🟡 WARNING: Version still 0.1.0 in installer

**Cause**: Version files not in sync before tagging.

**Solution**: Run preflight locally before tagging. Use `bump-version.js` script.

### 🟡 WARNING: NSIS installer shows "Error" during upgrade

**Cause**: Old process still running.

**Solution**: Add NSIS installer hooks to kill old processes.

### 🟡 WARNING: beforeBuildCommand fails on Windows

**Cause**: Using `cd ../../frontend && npm run build` (drive change issue).

**Solution**: Use Tauri v2's `cwd` property: `{ "script": "npm run build", "cwd": "../../frontend" }`.

### 🟡 WARNING: Startup screen shows error immediately on connection refused

**Cause**: The `catch` block in `startup/page.tsx` treats `ECONNREFUSED` as a fatal error and shows error + retry button immediately, when the sidecar just needs more time to start (PyInstaller takes 5-15s).

**Solution**: Never show error on `ECONNREFUSED`. Catch ALL exceptions silently and keep retrying for the full duration (60s). Only show error when ALL attempts fail:

```typescript
} catch {
    // Sidecar not ready yet (ECONNREFUSED, timeout, etc.):
    // keep retrying — only show error after ALL 60 attempts fail.
}
```

### 🟡 WARNING: Second instance creates duplicate tray icons

**Cause**: Running the app a second time creates a new process (and a new system tray icon), leading to multiple tray icons in the taskbar.

**Solution**: Use `tauri-plugin-single-instance` to prevent multiple instances:

```rust
// In Cargo.toml
tauri-plugin-single-instance = "2"

// In lib.rs .setup()
#[cfg(desktop)]
{
    app.handle().plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
        let _ = app.get_webview_window("main")
            .expect("no main window")
            .set_focus();
    })).expect("failed to register single-instance plugin");
}
```

### 🟡 WARNING: Duplicate sidecar processes on restart

**Cause**: If the app crashes and restarts, the old sidecar process may still be running on port 7723, and a new one is spawned on top.

**Solution**: Check if port 7723 is already responding before spawning:

```rust
fn start_sidecar(app: &tauri::App) {
    use std::net::TcpStream;
    let already_running = TcpStream::connect_timeout(
        &"127.0.0.1:7723".parse().unwrap(),
        std::time::Duration::from_millis(500),
    ).is_ok();
    if already_running {
        log::info!("Sidecar già in esecuzione — skip spawn.");
        return;
    }
    // ... spawn sidecar ...
}
```

## Optimization Tips

### Build time reduction

| Technique                                        | Time saved | Notes                                      |
| ------------------------------------------------ | ---------- | ------------------------------------------ |
| Remove `beforeBuildCommand` from tauri.conf.json | ~1-2 min   | Build frontend as explicit CI step instead |
| Build frontend separately in CI                  | ~1-2 min   | Parallel with sidecar build                |
| `--strip` on PyInstaller                         | ~30s       | Reduces binary size 20-30%, no extra deps  |
| `@tauri-apps/cli` via npm (not cargo install)    | ~12 min    | Precompiled, no compilation                |
| `Swatinem/rust-cache` with workspaces path       | ~8 min     | Caches target/ directory                   |
| `cache: "npm"` on setup-node                     | ~1 min     | Caches node_modules                        |
| `cache: "pip"` on setup-python                   | ~30s       | Caches pip packages                        |

### Expected build times (with all optimizations)

| OS      | Cold (first run) | Subsequent runs |
| ------- | ---------------- | --------------- |
| macOS   | ~15 min          | ~5 min          |
| Windows | ~25 min          | ~10 min         |
| Linux   | ~25 min          | ~13 min         |

### Sidecar size optimization

- Use `--strip` flag in PyInstaller: removes debug symbols from .so/.dll/.pyd files (20-30% size reduction)
- UPX compression can reduce further (50-70%) but requires `upx` binary on all 3 OS in CI
- PyInstaller `--onefile` bundles everything into a single binary — consider `--onedir` for faster startup (but more files)

## Troubleshooting Flowchart

### Release fails on macOS

```
Q: What's the error?
├── "npm error could not determine executable to run"
│   → Fix: Use npm --prefix ../frontend exec tauri build -- --ci from src-tauri/
├── "sidecar binary not found"
│   → Fix: Use rustc -vV for dynamic target triple detection
├── "cargo binstall" fails with 403
│   → Fix: Use @tauri-apps/cli as npm devDependency
└── "cargo install" takes too long
    → Fix: Use @tauri-apps/cli as npm devDependency
```

### Release fails on Windows

```
Q: What's the error?
├── ParserError / PowerShell syntax error
│   → Fix: Add shell: bash to the step
├── "npm error could not determine executable to run"
│   → Fix: Use npm --prefix ../frontend exec tauri build -- --ci
└── Rust toolchain install timeout
    → Fix: Re-run the workflow (GitHub runner transient issue)
```

### Release fails on Linux

```
Q: What's the error?
├── libwebkit2gtk-4.1-dev not found
│   → Fix: sudo apt-get update before install
├── "cargo build" fails — missing dependencies
│   → Fix: Install all packages listed in Step 9
├── "npm ci" fails
│   → Fix: Check package-lock.json and @swc/helpers version
└── Artifact too large (>500MB AppImage)
    → Fix: Use --strip in PyInstaller. Add UPX compression in CI.
```

### Startup issues

```
Q: App shows "Impossibile contattare il backend" immediately on launch
└── Cause: ECONNREFUSED triggers fatal error before sidecar is ready
    → Fix: Catch ALL exceptions silently (remove ECONNREFUSED special case).
          Keep retrying for all 60 attempts. Error only after all 60 fail.

Q: Multiple system tray icons appear
└── Cause: Second instance of app creates new process + new tray icon
    → Fix: Add tauri-plugin-single-instance to prevent duplicate instances.

Q: Two fastapi-sidecar processes in Task Manager
└── Cause: Old sidecar from crashed app still runs on port 7723
    → Fix: Check port 7723 with TcpStream::connect_timeout before spawning.
```

## FAQ

**Q: How to build for only one OS?**
A: Modify the `matrix.os` in `release.yml`.

**Q: How to enable auto-update?**
A: Set `TAURI_PRIVATE_KEY` and `TAURI_KEY_PASSWORD` secrets. Generate with `cargo tauri signer generate`.

**Q: Frontend not working in Tauri webview?**
A: Ensure `ALLOWED_ORIGINS` includes `tauri://localhost` and `https://tauri.localhost` for CORS.

**Q: Should I use cargo install or cargo binstall for tauri-cli?**
A: Neither. Use `@tauri-apps/cli` as an npm devDependency. It's faster, avoids rate limiting, and works on all platforms including ARM macOS.

**Q: Can I use tauri-action for GitHub CI?**
A: `tauri-apps/tauri-action` is a wrapper. We don't use it because we need fine-grained control over the multi-job pipeline (sidecar, rename, etc.). We use `@tauri-apps/cli` directly and `softprops/action-gh-release`.

**Q: Should I use beforeBuildCommand in tauri.conf.json?**
A: **Keep it for local development** (`cargo tauri dev` needs it), but **remove it in CI**. In CI, build the frontend as an explicit step BEFORE running `tauri build`. This makes the frontend build happen in parallel with other steps (sidecar build, Rust compilation) instead of sequentially inside `tauri build`. Saves 1-2 minutes per build.
