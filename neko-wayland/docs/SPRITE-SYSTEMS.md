# Sprite System Design

Understanding different sprite systems for neko-wayland.

Made with 💜 by Ada & Luna - Ada Research Foundation

## Classic Neko Sprite Sheets

Traditional desktop pets use a **grid-based sprite sheet**:

```
[sit1][sit2][yawn1][yawn2][scratch1][scratch2]...
[alert1][alert2][sleep1][sleep2]...
[runN1][runN2][runNE1][runNE2][runE1][runE2]...
...
```

- Fixed grid (e.g., 32x32 pixels per sprite)
- Row/column indexing
- All frames same size
- Simple to implement

## VPet Sprite System

VPet uses a more flexible **folder-based system**:

### File Organization
```
pet_name/
  happy/
    default_b_loop/
      frame_001_125.png
      frame_002_125.png
      frame_003_125.png
    touch_head_a_start/
      frame_001_100.png
      frame_002_100.png
    touch_head_b_loop/
      ...
    touch_head_c_end/
      ...
  nomal/
    ...
  poorcondition/
    ...
  ill/
    ...
```

### Naming Convention

**Folder names**: `{type}_{animat}`
- `type`: Animation type (default, touch_head, sleep, work, etc.)
- `animat`: Animation phase
  - `single`: One-shot animation
  - `a_start` / `b_loop` / `c_end`: Three-phase animation

**File names**: `frame_{number}_{duration}.png`
- `number`: Frame index (001, 002, 003...)
- `duration`: Frame duration in milliseconds

### Mood States

Four mood folders:
- `happy`: Happy/energetic
- `nomal`: Normal/default
- `poorcondition`: Tired/low energy
- `ill`: Sick/unwell

### Animation Types

VPet defines many animation types:
- `default`: Breathing/idle (required)
- `raised_static`: Being held (required)
- `raised_dynamic`: Being dragged (required)
- `sleep`: Sleeping (required)
- `say`: Talking (required)
- `work`: Working (required)
- `startup`: Boot animation (required)
- `move`: Walking/moving
- `touch_head`: Head petting
- `touch_body`: Body petting
- `idel`: Idle animations
- And many more!

### Performance Optimization

VPet combines all frames into one **horizontal strip** and caches it:
```
[frame1][frame2][frame3][frame4]...
```

Then uses margin offsets to slide the image and show different frames. This is faster than loading individual PNGs each frame.

## Our Hybrid Approach

For neko-wayland, we'll support BOTH systems:

### 1. Classic Grid Sprite Sheets
```rust
SpriteSheet::from_grid("neko.png", 32, 32, 8, 4)
```
- Simple, traditional
- Good for pixel art
- Easy to create

### 2. VPet-Style Folders
```rust
SpriteSheet::from_vpet_folder("pet_name/")
```
- Flexible frame sizes
- Per-frame timing
- Mood states
- Three-phase animations (start/loop/end)

### 3. Cairo Fallback
If no sprites are provided, use our beautiful cairo-drawn pets!

## DSL Integration

The `.neko` DSL can specify sprites:

```neko
pet my_cat {
    sprites: "path/to/sprites/"
    sprite_type: vpet  # or "grid"
    
    # Grid sprite sheet
    # sprites: "neko.png"
    # sprite_type: grid
    # sprite_size: 32x32
    # sprite_cols: 8
    # sprite_rows: 4
    
    wander {
        sprite: "move"  # Uses move animation
    }
    
    sleep {
        sprite: "sleep"  # Uses sleep animation (start/loop/end)
    }
}
```

## Implementation Plan

1. Keep cairo drawing as default/fallback
2. Add `SpriteSheet` trait with two implementations:
   - `GridSpriteSheet`: Classic grid-based
   - `VPetSpriteSheet`: Folder-based with timing
3. Integrate with DSL runtime
4. Support both in main app

This gives us maximum flexibility while staying simple for beginners!
