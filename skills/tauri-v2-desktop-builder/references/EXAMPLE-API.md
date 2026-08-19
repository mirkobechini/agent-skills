# API / Dependency Reference

## Tauri v2 API (Rust)

**Purpose**: Core framework for building the desktop app shell. Manages windows, events, system tray, and plugin lifecycle.

**Version**: `2.x` (latest stable)

**Installation**: Via `Cargo.toml` — see SKILL.md Step 3.

**Official Documentation**: https://v2.tauri.app/reference/

### Common APIs

#### `app.shell().sidecar("name")`

```rust
use tauri_plugin_shell::ShellExt;

let (mut rx, child) = app.shell()
    .sidecar("fastapi-sidecar")
    .unwrap()
    .spawn()
    .unwrap();
```

**Parameters**:

- `name` (string) — Name of the sidecar binary (without target triple suffix)

**Returns**: `(CommandChild, Receiver<CommandEvent>)`

#### `app.get_webview_window("main")`

```rust
let window = app.get_webview_window("main").expect("no main window");
window.set_focus().ok();
```

**Returns**: `Option<WebviewWindow>`

#### `TrayIconBuilder`

```rust
use tauri::tray::{TrayIconBuilder, TrayIconEvent};
use tauri::menu::{Menu, MenuItem};

TrayIconBuilder::new()
    .icon(app.default_window_icon().unwrap().clone())
    .tooltip("App Name")
    .menu(&menu)
    .on_menu_event(|app, event| { /* ... */ })
    .build()?;
```

### Error Handling

| Error                                      | Cause                                                      | Solution                         |
| ------------------------------------------ | ---------------------------------------------------------- | -------------------------------- |
| `no method 'shell' found`                  | Missing `use tauri_plugin_shell::ShellExt;`                | Add the import                   |
| `borrowed value does not live long enough` | Using `app.state::<T>()` instead of `app.try_state::<T>()` | Use `try_state` + local variable |

---

## PyInstaller

**Purpose**: Bundle the FastAPI backend into a single executable (sidecar) for distribution.

**Version**: `6.x` (latest stable)

**Installation**: `pip install pyinstaller`

**Official Documentation**: https://pyinstaller.org/en/stable/

### Common Flags

| Flag                     | Purpose                                                       |
| ------------------------ | ------------------------------------------------------------- |
| `--onefile`              | Bundle everything into a single executable                    |
| `--noconsole`            | Suppress terminal window on Windows (release builds)          |
| `--paths DIR`            | Add directory to Python module search path                    |
| `--hidden-import MODULE` | Force inclusion of a module not detected automatically        |
| `--collect-all PACKAGE`  | Collect all data files and submodules for a package           |
| `--add-data SRC:DST`     | Add non-Python files (use `;` on Windows, `:` on macOS/Linux) |
| `--runtime-tmpdir DIR`   | Set temp directory for extraction at runtime                  |
| `--strip`                | Strip debug symbols (20-30% size reduction)                   |

### Error Handling

| Error                                              | Cause                           | Solution                                    |
| -------------------------------------------------- | ------------------------------- | ------------------------------------------- |
| `ModuleNotFoundError: No module named 'fastapi'`   | PyInstaller can't trace imports | Use `--paths ../backend` to point to source |
| `RecursionError: maximum recursion depth exceeded` | Deep dependency tree            | Add `--recursionlimit 5000`                 |

---

## rustc (Rust Compiler)

**Purpose**: Detect the host target triple for sidecar binary naming.

**Version**: Stable (latest)

**Installation**: Via `rustup`

### Common Commands

#### Detect host triple

```bash
rustc -vV | grep "^host:" | awk '{print $2}'
```

**Output example**: `x86_64-pc-windows-msvc`

### Target Triples

| Platform    | Triple                     |
| ----------- | -------------------------- |
| Windows x64 | `x86_64-pc-windows-msvc`   |
| macOS ARM   | `aarch64-apple-darwin`     |
| macOS Intel | `x86_64-apple-darwin`      |
| Linux x64   | `x86_64-unknown-linux-gnu` |

---

## NSIS (Nullsoft Scriptable Install System)

**Purpose**: Create Windows installers for the Tauri app.

**Version**: 3.x (bundled with Tauri)

### Installer Hooks (`installer.nsh`)

```nsis
!macro customInstall
  nsExec::ExecToStack 'taskkill /F /IM "${PRODUCT_NAME}.exe" 2>NUL'
!macroend

!macro customUnInstall
  nsExec::ExecToStack 'taskkill /F /IM "${PRODUCT_NAME}.exe" 2>NUL'
!macroend
```

**Purpose**: Kill any running instance before install/upgrade to prevent "Error" dialog.

---

## GitHub Actions

**Purpose**: CI/CD pipeline for building and releasing the desktop app.

### Key Actions

| Action                        | Version   | Purpose                                     |
| ----------------------------- | --------- | ------------------------------------------- |
| `actions/checkout`            | `@v5`     | Check out repository                        |
| `actions/setup-node`          | `@v5`     | Install Node.js with npm cache              |
| `actions/setup-python`        | `@v5`     | Install Python with pip cache               |
| `dtolnay/rust-toolchain`      | `@stable` | Install Rust with cross-compilation targets |
| `swatinem/rust-cache`         | `@v2`     | Cache Rust `target/` directory              |
| `actions/upload-artifact`     | `@v4`     | Upload build artifacts                      |
| `actions/download-artifact`   | `@v4`     | Download build artifacts                    |
| `softprops/action-gh-release` | `@v2`     | Create GitHub Release                       |

### Secrets

| Secret               | Purpose                                                                    |
| -------------------- | -------------------------------------------------------------------------- |
| `TAURI_PRIVATE_KEY`  | Signing key for auto-updates (generate with `cargo tauri signer generate`) |
| `TAURI_KEY_PASSWORD` | Password for the signing key                                               |
