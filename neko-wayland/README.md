# neko-wayland 🐱

A cute desktop pet for Wayland/Hyprland - classic neko.exe behavior!

**Made with 💜 by Ada & Luna**

## What is this?

Remember neko.exe? The little cat that chased your cursor around Windows 95? This is that, but for modern Wayland compositors like Hyprland!

Uses `gtk4-layer-shell` for proper overlay rendering that works with Wayland's security model.

## Features

- 🐱 Classic neko behavior: chases cursor, sleeps when idle
- 🎨 Sprite sheet support for custom neko skins
- 🖥️ Native Wayland via gtk4-layer-shell
- 💤 Sleep/wake animations
- 🏃 8-directional running animations
- 🧹 Idle behaviors: sitting, yawning, scratching, washing

## Building

### Dependencies

```bash
# Arch/Manjaro
sudo pacman -S gtk4 gtk4-layer-shell rust

# Fedora
sudo dnf install gtk4-devel gtk4-layer-shell-devel rust cargo

# Ubuntu/Debian (may need PPA for gtk4-layer-shell)
sudo apt install libgtk-4-dev rust cargo
# gtk4-layer-shell may need to be built from source
```

### Build

```bash
cargo build --release
```

### Run

```bash
./target/release/neko-wayland
```

## Configuration

TODO: Config file support

## Sprite Sheets

The classic neko sprite sheet layout:

```
Row 0: Sit(2), Yawn(2), Scratch(2), Wash(2)
Row 1: Alert(2), Sleep(2), [unused]
Row 2: RunN(2), RunNE(2), RunE(2), RunSE(2)
Row 3: RunS(2), RunSW(2), RunW(2), RunNW(2)
```

Each sprite is 32x32 pixels. Numbers in parentheses indicate animation frames.

## Roadmap

- [ ] Cursor tracking (Wayland pointer protocols)
- [ ] Config file (TOML)
- [ ] Multiple sprite sheet support
- [ ] Click interactions
- [ ] Speech bubbles (for Ada integration!)
- [ ] Sound effects

## Why?

This is a stepping stone towards porting VPet to Linux! We're learning the gtk4-layer-shell stack in a minimal context before tackling the full VPet port.

Also, neko is just cute. 🐱

## License

MIT

## See Also

- [wayland-vpets](https://github.com/furudbat/wayland-vpets) - Similar project in C
- [VPet](https://github.com/LorisYounger/VPet) - The full desktop pet we're eventually porting
- [gtk4-layer-shell](https://github.com/wmww/gtk4-layer-shell) - The magic that makes this work
