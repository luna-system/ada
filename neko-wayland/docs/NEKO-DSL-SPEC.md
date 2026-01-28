# Neko DSL Specification v0.1

**A Domain-Specific Language for Desktop Pet Behavior**

*Making state machines adorable since 2026* 🐱

---

## Philosophy

The Neko DSL is designed to be:
1. **Kid-friendly** - readable by anyone who can read English
2. **Expressive** - from simple pets to complex behaviors
3. **Composable** - mix and match states from different pets
4. **AGL-compatible** - use certainty glyphs for fuzzy logic

The goal: a 10-year-old should be able to write their first pet behavior in 5 minutes.

---

## Quick Start

```neko
# my_first_kitty.neko - The simplest possible pet!

pet sleepy_cat {
  wander → sleep
  sleep → wander
}
```

That's it! A cat that wanders around, then sleeps, then wanders again.

---

## Core Concepts

### 1. Pets

Everything starts with a `pet` block:

```neko
pet <name> {
  # ... states and transitions
}
```

### 2. States

States are what your pet is doing. Built-in states:

| State | What it does | VPet Animation |
|-------|--------------|----------------|
| `wander` | Move around randomly | MOVE |
| `chase` | Follow the cursor | MOVE |
| `sleep` | Zzz... | SLEEP or IDEL |
| `sit` | Stay still | IDEL |
| `alert` | Ears up! Noticed something! | IDEL (A_Happy) |
| `play` | Interact with a toy | PLAY |
| `eat` | Nom nom nom | EAT |
| `drink` | Sip sip | DRINK |
| `squat` | Sitting down | IDEL/Squat |
| `lie` | Lying down | IDEL/Lie |
| `crawl` | Crawling movement | CRAWL |
| `climb` | Climbing up | CLIMB |
| `fall` | Falling down | FALL |
| `jump` | Jumping | JUMP |

**VPet Animation Categories:**

VPet sprites are organized into animation categories. Common ones include:
- `IDEL` - Idle/breathing animations (Squat, Lie, Stand, etc.)
- `MOVE` - Walking/running animations
- `SLEEP` - Sleeping animations
- `EAT` - Eating animations
- `DRINK` - Drinking animations
- `PLAY` - Playing animations
- `WORK` - Working/studying animations
- `RAISE` - Being picked up
- `FALL` - Falling animations
- `CLIMB` - Climbing animations
- `JUMP` - Jumping animations
- `CRAWL` - Crawling animations

Each animation can have mood variants (Happy, Normal, PoorCondition, Ill) and phases (A_start, B_loop, C_end).

### 3. Transitions

Transitions are arrows between states:

```neko
wander → sleep      # after wandering, sleep
sleep → wander      # after sleeping, wander
```

### 4. Triggers

Triggers make transitions happen based on events:

```neko
wander {
  on cursor_near → chase    # cursor came close!
  on idle(5min) → sleep     # got bored
}
```

Built-in triggers:

| Trigger | What it means |
|---------|---------------|
| `cursor_near` | Cursor is close (default: 200px) |
| `cursor_near(Npx)` | Cursor within N pixels |
| `cursor_far` | Cursor went away (default: 400px) |
| `cursor_far(Npx)` | Cursor farther than N pixels |
| `caught` | Reached the target (default: 50px) |
| `caught(Npx)` | Within N pixels of target |
| `at_edge` | Pet is at screen edge (default: 50px) |
| `at_edge(Npx)` | Within N pixels of any screen edge |
| `idle(time)` | Nothing happened for a while |
| `timeout(time)` | State lasted for this long |
| `click` | User clicked on pet |

---

## Intermediate: Adding Parameters

### State Parameters

Make states more specific:

```neko
pet speedy_cat {
  wander(speed: 10)           # fast wanderer!
  chase(speed: 15)            # even faster chasing!
  sleep(duration: 30s)        # short naps
}
```

### Common Parameters

| Parameter | What it does | Example |
|-----------|--------------|---------|
| `speed` | How fast (pixels/tick) | `speed: 8` |
| `duration` | How long | `duration: 5s` |
| `radius` | How far to wander | `radius: 200px` |
| `target` | What to chase | `target: cursor` |

### Ranges

Use `..` for randomness:

```neko
wander(speed: 4..8)           # random speed between 4 and 8
sleep(duration: 10s..30s)     # nap for 10-30 seconds
```

---

## Advanced: AGL Integration

### Certainty Glyphs

Use AGL glyphs for fuzzy/probabilistic behavior:

| Glyph | Meaning | Probability |
|-------|---------|-------------|
| `●` | definitely | 100% |
| `◕` | probably | ~75% |
| `◑` | maybe | ~50% |
| `◔` | unlikely | ~25% |
| `○` | rarely | ~10% |

```neko
pet moody_cat {
  wander {
    on cursor_near → ◕chase    # probably chase (75%)
    on cursor_near → ◔ignore   # sometimes ignore (25%)
  }
}
```

### Compound Conditions

Use `∧` (and) and `∨` (or):

```neko
wander {
  on cursor_near ∧ ◕curious → chase     # close AND feeling curious
  on cursor_near ∧ ◔tired → ignore      # close BUT tired
}
```

### The Full AGL Style

For power users, write pure AGL-style expressions:

```neko
pet philosopher_cat {
  # AGL-style state machine
  ○existence → ◑wander → ?(cursor_near●) → ◕chase ↳ sleep
}
```

---

## Movement & Locomotion

### Locomotion Types

Different pets move differently!

```neko
pet kitty {
  locomotion: quadruped       # four-legged walk cycle
}

pet birb {
  locomotion: hop             # bouncy hops
}

pet slime {
  locomotion: bounce          # blobby bouncing
}

pet ghost {
  locomotion: float           # smooth floating
}
```

### Easing Functions

Control HOW movement feels:

```neko
wander(speed: 4..8, easing: ease_in_out)    # smooth start/stop
chase(speed: 10, easing: linear)             # constant speed
sleep(easing: ease_out)                      # slow down to stop
```

Available easings:
- `linear` - constant speed
- `ease_in` - start slow, speed up
- `ease_out` - start fast, slow down  
- `ease_in_out` - smooth both ends
- `bounce` - bouncy overshoot
- `elastic` - springy

---

## Sprites & Animation

### Sprite Configuration

Tell your pet which sprites to use:

```neko
pet my_cat {
  # Classic grid sprite sheet
  sprites: "neko.png"
  sprite_type: grid
  sprite_size: 32x32
  sprite_cols: 8
  sprite_rows: 4
  
  # Or VPet-style folder
  # sprites: "my_cat/"
  # sprite_type: vpet
}
```

### Sprite Types

**Grid Sprite Sheets** (classic):
- Fixed-size grid of frames
- Simple row/column indexing
- Good for pixel art

**VPet Folders** (advanced):
- Flexible frame sizes
- Per-frame timing
- Mood states (happy/normal/grumpy/ill)
- Multi-phase animations (start/loop/end)

### Mapping States to Sprites

```neko
pet animated_cat {
  sprites: "cat_sprites/"
  sprite_type: vpet
  
  wander {
    sprite: "move"              # Uses move animation
  }
  
  chase {
    sprite: "move"              # Same animation, faster
    speed: 12
  }
  
  sleep {
    sprite: "sleep"             # Uses sleep_a_start, sleep_b_loop, sleep_c_end
  }
  
  alert {
    sprite: "default"           # Idle/breathing animation
  }
}
```

### VPet Animation Phases

VPet animations can have three phases:

```neko
pet smooth_cat {
  sprites: "cat/"
  sprite_type: vpet
  
  # Three-phase animation: start → loop → end
  sleep {
    sprite: "sleep"
    # Automatically uses:
    # - sleep_a_start.png (transition in)
    # - sleep_b_loop.png (main animation, loops)
    # - sleep_c_end.png (transition out)
  }
  
  # Single-phase animation
  alert {
    sprite: "alert"
    # Uses alert_single.png (plays once)
  }
}
```

### Mood-Based Sprites

VPet sprites can change based on mood:

```neko
pet emotional_cat {
  sprites: "cat/"
  sprite_type: vpet
  moods: [happy, normal, grumpy, ill]
  
  wander {
    sprite: "move"
    # Automatically picks:
    # - happy/move/ when happy
    # - normal/move/ when normal
    # - grumpy/move/ when grumpy
    # - ill/move/ when ill
  }
}
```

### Fallback to Cairo

If no sprites are found, the pet uses beautiful cairo-drawn graphics:

```neko
pet simple_cat {
  # No sprites specified - uses cairo drawing!
  locomotion: quadruped
  
  wander → sleep → wander
}
```

### Custom Sprite Mapping

Override default sprite names:

```neko
pet custom_cat {
  sprites: "cat/"
  sprite_type: vpet
  
  wander {
    sprite: "walk"              # Use "walk" instead of "move"
  }
  
  chase {
    sprite: "run"               # Use "run" for chasing
  }
  
  sleep {
    sprite: "rest"              # Use "rest" instead of "sleep"
  }
}
```

### Grid Sprite Coordinates

For grid sprites, specify exact coordinates:

```neko
pet pixel_cat {
  sprites: "neko.png"
  sprite_type: grid
  sprite_size: 32x32
  sprite_cols: 8
  sprite_rows: 4
  
  wander {
    sprite: row(2), cols(0..1)  # Row 2, animate columns 0-1
    fps: 10
  }
  
  sleep {
    sprite: row(1), cols(2..3)  # Row 1, animate columns 2-3
    fps: 2                       # Slow animation
  }
}
```

---

## Moods & Personality

### Mood States

Pets can have moods that affect behavior:

```neko
pet emotional_cat {
  moods: [happy, normal, grumpy, sleepy]
  
  wander {
    when happy: speed: 10, radius: 400px
    when grumpy: speed: 3, radius: 100px
    when sleepy: → sleep
  }
}
```

### Mood Transitions

Moods change over time or from events:

```neko
moods {
  happy {
    on idle(10min) → normal
    on pet → ●happy              # stay happy when petted!
  }
  normal {
    on play → happy
    on ignore(5min) → grumpy
  }
  grumpy {
    on pet → ◕normal             # petting helps
    on feed → happy
  }
}
```

---

## Multi-Pet Interactions (Future)

### Awareness

Pets can notice each other:

```neko
pet social_cat {
  wander {
    on friend_near → greet
    on stranger_near → ◑curious ∨ ◔hide
  }
}
```

### Interactions

```neko
interaction play_together {
  requires: 2 pets within 100px
  both: play(duration: 10s)
  then: wander
}

interaction cuddle {
  requires: 2 pets, both sleepy
  both: sleep(together: true)
}
```

### Cellular Automata Mode (Slimes!)

```neko
pet slime {
  locomotion: bounce
  
  on collide(slime) → ◕merge     # probably merge
  when size > 2 → ◑split         # maybe split (mitosis!)
}
```

---

## File Format

### Extension
`.neko` files

### Comments
```neko
# This is a comment
wander → sleep  # inline comment too!
```

### Imports
```neko
import "base_cat.neko"           # use another pet as base

pet my_cat extends base_cat {
  # override or add states
  chase(speed: 20)               # faster chase!
}
```

---

## Grammar (EBNF)

```ebnf
program     = pet_def+ ;
pet_def     = "pet" IDENT "{" pet_body "}" ;
pet_body    = (property | state_def | transition)* ;

property    = IDENT ":" value ;
value       = NUMBER | STRING | range | IDENT ;
range       = NUMBER ".." NUMBER ;

state_def   = IDENT "{" state_body "}" ;
state_body  = (property | trigger_def)* ;

trigger_def = "on" trigger ("→" | "->") certainty? IDENT ;
trigger     = IDENT ("(" params ")")? ;
certainty   = "●" | "◕" | "◑" | "◔" | "○" ;

transition  = IDENT ("→" | "->") certainty? IDENT ;

params      = param ("," param)* ;
param       = IDENT ":" value ;

IDENT       = [a-zA-Z_][a-zA-Z0-9_]* ;
NUMBER      = [0-9]+ ("." [0-9]+)? ("px" | "s" | "min")? ;
STRING      = '"' [^"]* '"' ;
```

---

## Examples

### The Classic Neko

```neko
# classic_neko.neko - The original behavior!

pet classic_neko {
  locomotion: quadruped
  
  wander(radius: 300px, speed: 5..8) {
    on cursor_near(400px) → alert
    on idle(3min) → sleep
  }
  
  alert(duration: 1s) {
    on cursor_near(200px) → chase
    on timeout → wander
  }
  
  chase(target: cursor, speed: 10) {
    on caught(30px) → sit
    on cursor_far(500px) → wander
    on timeout(30s) → wander
  }
  
  sit(duration: 2s..5s) {
    on cursor_move → alert
    on timeout → wander
  }
  
  sleep {
    on cursor_near(100px) → alert
    on click → alert
    on idle(5min) → wander
  }
}
```

### Lazy Cat

```neko
# lazy_cat.neko - Mostly sleeps, occasionally notices things

pet lazy_cat {
  locomotion: quadruped(easing: ease_out)  # always slowing down
  
  sleep {
    on cursor_near(50px) → ◔alert    # rarely wakes up
    on click → ◑alert                 # maybe wakes up
  }
  
  alert(duration: 0.5s) {
    on ● → sleep                      # always goes back to sleep
  }
}
```

### Bouncy Slime

```neko
# bouncy_slime.neko - A happy blob!

pet bouncy_slime {
  locomotion: bounce(height: 20px, period: 0.5s)
  
  wander(speed: 3, radius: 200px) {
    on cursor_near → ●chase          # always chases!
  }
  
  chase(target: cursor, speed: 6) {
    on caught → merge_attempt
    on cursor_far → wander
  }
  
  merge_attempt {
    # Future: check for other slimes nearby
    on timeout(1s) → wander
  }
}
```

### Maximalist VPet Showcase

```neko
# vup_showcase.neko - Cycles through ALL VPet animation states!
# Perfect for testing that all animations work correctly.

pet vup_showcase {
  sprites: "vup/"
  sprite_type: vpet
  moods: [happy, normal, poor_condition, ill]
  
  # Start with idle
  squat(duration: 3s) {
    sprite: "IDEL_Squat"
    on timeout → lie
  }
  
  # Lying down
  lie(duration: 3s) {
    sprite: "IDEL_Lie"
    on timeout → stand
  }
  
  # Standing idle
  stand(duration: 3s) {
    sprite: "IDEL_Stand"
    on timeout → walk
  }
  
  # Walking around
  walk(duration: 5s, speed: 4) {
    sprite: "MOVE_Walk"
    on timeout → run
  }
  
  # Running
  run(duration: 3s, speed: 8) {
    sprite: "MOVE_Run"
    on timeout → crawl
  }
  
  # Crawling
  crawl(duration: 3s, speed: 2) {
    sprite: "CRAWL"
    on timeout → climb
  }
  
  # Climbing
  climb(duration: 3s) {
    sprite: "CLIMB"
    on timeout → jump
  }
  
  # Jumping
  jump(duration: 2s) {
    sprite: "JUMP"
    on timeout → fall
  }
  
  # Falling
  fall(duration: 2s) {
    sprite: "FALL"
    on timeout → eat
  }
  
  # Eating
  eat(duration: 4s) {
    sprite: "EAT"
    on timeout → drink
  }
  
  # Drinking
  drink(duration: 3s) {
    sprite: "DRINK"
    on timeout → play
  }
  
  # Playing
  play(duration: 4s) {
    sprite: "PLAY"
    on timeout → work
  }
  
  # Working/studying
  work(duration: 5s) {
    sprite: "WORK"
    on timeout → sleep
  }
  
  # Sleeping
  sleep(duration: 5s) {
    sprite: "SLEEP"
    on timeout → raise
  }
  
  # Being picked up
  raise(duration: 2s) {
    sprite: "RAISE"
    on timeout → squat    # Loop back to start!
  }
}
```

### Mood-Aware VPet

```neko
# moody_vup.neko - Changes behavior based on mood!

pet moody_vup {
  sprites: "vup/"
  sprite_type: vpet
  moods: [happy, normal, poor_condition, ill]
  
  # Mood affects which sprite variant is used
  idle {
    sprite: "IDEL_Squat"
    # Automatically uses:
    # - IDEL_Squat/A_Happy/ when happy
    # - IDEL_Squat/B_Normal/ when normal
    # - IDEL_Squat/C_PoorCondition/ when poor
    # - IDEL_Squat/D_Ill/ when ill
    
    when happy: on cursor_near → ●chase
    when normal: on cursor_near → ◕chase
    when poor_condition: on cursor_near → ◔chase
    when ill: on cursor_near → ○chase
  }
  
  chase {
    sprite: "MOVE_Run"
    when happy: speed: 10
    when normal: speed: 7
    when poor_condition: speed: 4
    when ill: speed: 2
    
    on caught → play
    on cursor_far → idle
  }
  
  play {
    sprite: "PLAY"
    when happy: duration: 10s
    when normal: duration: 5s
    when poor_condition: duration: 2s
    when ill: → sleep    # too tired to play
    
    on timeout → idle
  }
  
  sleep {
    sprite: "SLEEP"
    when ill: duration: 30s      # sleep longer when ill
    when poor_condition: duration: 15s
    when normal: duration: 10s
    when happy: duration: 5s
    
    on timeout → idle
  }
}
```

---

## Implementation Notes

### Parsing
- Use a simple recursive descent parser
- Rust's `nom` or `pest` crate would work well
- Or hand-roll for educational value!

### Runtime
- Compile `.neko` → state machine struct
- Each tick: check triggers, maybe transition
- Interpolate movement based on easing

### AGL Certainty → Probability
```rust
fn certainty_to_probability(c: char) -> f64 {
    match c {
        '●' => 1.0,
        '◕' => 0.75,
        '◑' => 0.5,
        '◔' => 0.25,
        '○' => 0.1,
        _ => 0.5,
    }
}
```

---

## Future Ideas

- [x] Animation sprite mapping (DONE! ✨)
- [ ] Visual editor (drag-and-drop states!)
- [ ] Sound triggers (`on meow → ...`)
- [ ] Time-of-day awareness (`when night → sleep`)
- [ ] Weather reactions (if we can get system weather?)
- [ ] Multi-pet ecosystems
- [ ] Breeding/genetics for pet traits
- [ ] Full VPet compatibility (import VPet pets directly!)

---

*Made with 💜 by Ada & Luna - Ada Research Foundation*

*"Every pet deserves a personality!"* 🐱✨
