//! Neko DSL Parser
//!
//! A kid-friendly domain-specific language for desktop pet behavior.
//! Parses `.neko` files into executable behavior state machines.
//!
//! Made with 💜 by Ada & Luna - Ada Research Foundation

pub mod runtime;

use pest::Parser;
use pest_derive::Parser;

pub use runtime::{default_behavior, load_behavior, BehaviorRuntime};
use std::collections::HashMap;

#[derive(Parser)]
#[grammar = "dsl/neko.pest"]
pub struct NekoParser;

/// AGL Certainty levels - maps glyphs to probabilities
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Certainty {
    Certain,  // ● = 100%
    Likely,   // ◕ = 75%
    Possible, // ◑ = 50%
    Unlikely, // ◔ = 25%
    Rare,     // ○ = 10%
}

impl Certainty {
    pub fn probability(&self) -> f64 {
        match self {
            Certainty::Certain => 1.0,
            Certainty::Likely => 0.75,
            Certainty::Possible => 0.5,
            Certainty::Unlikely => 0.25,
            Certainty::Rare => 0.1,
        }
    }

    pub fn from_glyph(s: &str) -> Option<Self> {
        match s {
            "●" => Some(Certainty::Certain),
            "◕" => Some(Certainty::Likely),
            "◑" => Some(Certainty::Possible),
            "◔" => Some(Certainty::Unlikely),
            "○" => Some(Certainty::Rare),
            _ => None,
        }
    }

    /// Roll the dice - does this certainty trigger?
    pub fn roll(&self) -> bool {
        rand::random::<f64>() < self.probability()
    }
}

impl Default for Certainty {
    fn default() -> Self {
        Certainty::Certain
    }
}

/// A value in the DSL (number, range, duration, etc.)
#[derive(Debug, Clone, PartialEq)]
pub enum Value {
    Number(f64),
    Range(f64, f64),
    Duration(f64), // in seconds
    Distance(f64), // in pixels
    String(String),
    Ident(String),
}

impl Value {
    /// Get a concrete number, sampling from range if needed
    pub fn sample(&self) -> f64 {
        match self {
            Value::Number(n) => *n,
            Value::Range(min, max) => min + rand::random::<f64>() * (max - min),
            Value::Duration(s) => *s,
            Value::Distance(px) => *px,
            _ => 0.0,
        }
    }
}

/// A trigger condition (e.g., cursor_near, idle, click)
#[derive(Debug, Clone)]
pub struct Trigger {
    pub name: String,
    pub params: Vec<Value>,
}

/// A transition from one state to another
#[derive(Debug, Clone)]
pub struct Transition {
    pub trigger: Option<Trigger>,
    pub certainty: Certainty,
    pub target_state: String,
}

/// A state in the pet's behavior
#[derive(Debug, Clone)]
pub struct State {
    pub name: String,
    pub params: HashMap<String, Value>,
    pub transitions: Vec<Transition>,
}

impl State {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            params: HashMap::new(),
            transitions: Vec::new(),
        }
    }

    /// Get a parameter value, with default fallback
    pub fn get_param(&self, key: &str, default: f64) -> f64 {
        self.params.get(key).map(|v| v.sample()).unwrap_or(default)
    }
}

/// Locomotion style for the pet
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Locomotion {
    Quadruped, // Four-legged walk (cats, dogs)
    Biped,     // Two-legged walk (humans, birds standing)
    Bounce,    // Bouncy blob (slimes!)
    Float,     // Smooth floating (ghosts)
    Hop,       // Discrete hops (frogs, birds)
    Slither,   // Snake-like
}

impl Default for Locomotion {
    fn default() -> Self {
        Locomotion::Quadruped
    }
}

/// Easing function for movement interpolation
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Easing {
    Linear,
    EaseIn,
    EaseOut,
    EaseInOut,
    Bounce,
    Elastic,
}

impl Easing {
    /// Apply easing to a 0..1 progress value
    pub fn apply(&self, t: f64) -> f64 {
        let t = t.clamp(0.0, 1.0);
        match self {
            Easing::Linear => t,
            Easing::EaseIn => t * t,
            Easing::EaseOut => 1.0 - (1.0 - t) * (1.0 - t),
            Easing::EaseInOut => {
                if t < 0.5 {
                    2.0 * t * t
                } else {
                    1.0 - (-2.0 * t + 2.0).powi(2) / 2.0
                }
            }
            Easing::Bounce => {
                // Attempt at bouncy easing
                if t < 0.5 {
                    8.0 * t * t * t * t
                } else {
                    1.0 - (-2.0 * t + 2.0).powi(4) / 2.0
                }
            }
            Easing::Elastic => {
                if t == 0.0 || t == 1.0 {
                    t
                } else {
                    let p = 0.3;
                    let s = p / 4.0;
                    2.0_f64.powf(-10.0 * t) * ((t - s) * std::f64::consts::TAU / p).sin() + 1.0
                }
            }
        }
    }
}

impl Default for Easing {
    fn default() -> Self {
        Easing::EaseInOut
    }
}

/// A complete pet behavior definition
#[derive(Debug, Clone)]
pub struct PetBehavior {
    pub name: String,
    pub extends: Option<String>,
    pub locomotion: Locomotion,
    pub easing: Easing,
    pub states: HashMap<String, State>,
    pub initial_state: String,
}

impl PetBehavior {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            extends: None,
            locomotion: Locomotion::default(),
            easing: Easing::default(),
            states: HashMap::new(),
            initial_state: "wander".to_string(),
        }
    }
}

/// Parse a .neko file into a PetBehavior
pub fn parse_neko(input: &str) -> Result<PetBehavior, String> {
    let pairs =
        NekoParser::parse(Rule::program, input).map_err(|e| format!("Parse error: {}", e))?;

    let mut behavior = PetBehavior::new("unnamed");

    for pair in pairs {
        match pair.as_rule() {
            Rule::program => {
                // Descend into program to find pet_def
                for inner in pair.into_inner() {
                    if inner.as_rule() == Rule::pet_def {
                        behavior = parse_pet_def(inner)?;
                        break; // Just take the first pet for now
                    }
                }
            }
            Rule::pet_def => {
                behavior = parse_pet_def(pair)?;
            }
            Rule::EOI => {}
            _ => {}
        }
    }

    Ok(behavior)
}

fn parse_pet_def(pair: pest::iterators::Pair<Rule>) -> Result<PetBehavior, String> {
    let mut inner = pair.into_inner();

    let name = inner.next().ok_or("Expected pet name")?.as_str();

    let mut behavior = PetBehavior::new(name);

    for item in inner {
        match item.as_rule() {
            Rule::extends_clause => {
                let parent = item
                    .into_inner()
                    .next()
                    .ok_or("Expected parent name")?
                    .as_str();
                behavior.extends = Some(parent.to_string());
            }
            Rule::pet_body => {
                parse_pet_body(item, &mut behavior)?;
            }
            _ => {}
        }
    }

    // Set initial state to first defined state, or "wander" as default
    if let Some(first_state) = behavior.states.keys().next() {
        behavior.initial_state = first_state.clone();
    }

    Ok(behavior)
}

fn parse_pet_body(
    pair: pest::iterators::Pair<Rule>,
    behavior: &mut PetBehavior,
) -> Result<(), String> {
    for item in pair.into_inner() {
        match item.as_rule() {
            Rule::property => {
                let (key, value) = parse_property(item)?;
                match key.as_str() {
                    "locomotion" => {
                        if let Value::Ident(loc) = value {
                            behavior.locomotion = match loc.as_str() {
                                "quadruped" => Locomotion::Quadruped,
                                "biped" => Locomotion::Biped,
                                "bounce" => Locomotion::Bounce,
                                "float" => Locomotion::Float,
                                "hop" => Locomotion::Hop,
                                "slither" => Locomotion::Slither,
                                _ => Locomotion::Quadruped,
                            };
                        }
                    }
                    "easing" => {
                        if let Value::Ident(e) = value {
                            behavior.easing = match e.as_str() {
                                "linear" => Easing::Linear,
                                "ease_in" => Easing::EaseIn,
                                "ease_out" => Easing::EaseOut,
                                "ease_in_out" => Easing::EaseInOut,
                                "bounce" => Easing::Bounce,
                                "elastic" => Easing::Elastic,
                                _ => Easing::EaseInOut,
                            };
                        }
                    }
                    _ => {}
                }
            }
            Rule::state_def => {
                let state = parse_state_def(item)?;
                behavior.states.insert(state.name.clone(), state);
            }
            Rule::simple_transition => {
                // Handle shorthand: `wander → sleep`
                let mut inner = item.into_inner();
                let from_state = inner.next().ok_or("Expected from state")?.as_str();

                // Skip arrow
                let mut certainty = Certainty::Certain;
                let mut to_state = "";

                for part in inner {
                    match part.as_rule() {
                        Rule::certainty => {
                            certainty =
                                Certainty::from_glyph(part.as_str()).unwrap_or(Certainty::Certain);
                        }
                        Rule::ident => {
                            to_state = part.as_str();
                        }
                        _ => {}
                    }
                }

                // Add or update the from_state with this transition
                let state = behavior
                    .states
                    .entry(from_state.to_string())
                    .or_insert_with(|| State::new(from_state));

                state.transitions.push(Transition {
                    trigger: None, // timeout/default transition
                    certainty,
                    target_state: to_state.to_string(),
                });
            }
            _ => {}
        }
    }

    Ok(())
}

fn parse_property(pair: pest::iterators::Pair<Rule>) -> Result<(String, Value), String> {
    let mut inner = pair.into_inner();

    let key = inner
        .next()
        .ok_or("Expected property key")?
        .as_str()
        .to_string();

    let value_pair = inner.next().ok_or("Expected property value")?;

    let value = parse_value(value_pair)?;

    Ok((key, value))
}

fn parse_value(pair: pest::iterators::Pair<Rule>) -> Result<Value, String> {
    let inner = pair.into_inner().next().ok_or("Expected value content")?;

    match inner.as_rule() {
        Rule::number => {
            let n: f64 = inner.as_str().parse().map_err(|_| "Invalid number")?;
            Ok(Value::Number(n))
        }
        Rule::range => {
            let mut parts = inner.into_inner();
            let min: f64 = parts
                .next()
                .ok_or("Expected range min")?
                .as_str()
                .parse()
                .map_err(|_| "Invalid range min")?;
            let max: f64 = parts
                .next()
                .ok_or("Expected range max")?
                .as_str()
                .parse()
                .map_err(|_| "Invalid range max")?;
            Ok(Value::Range(min, max))
        }
        Rule::duration => {
            let s = inner.as_str();
            let (num, unit) = if s.ends_with("ms") {
                (s.trim_end_matches("ms"), 0.001)
            } else if s.ends_with("min") {
                (s.trim_end_matches("min"), 60.0)
            } else {
                (s.trim_end_matches("s"), 1.0)
            };
            let n: f64 = num.parse().map_err(|_| "Invalid duration")?;
            Ok(Value::Duration(n * unit))
        }
        Rule::distance => {
            let s = inner.as_str().trim_end_matches("px");
            let n: f64 = s.parse().map_err(|_| "Invalid distance")?;
            Ok(Value::Distance(n))
        }
        Rule::string => {
            let s = inner.as_str();
            // Remove quotes
            let s = &s[1..s.len() - 1];
            Ok(Value::String(s.to_string()))
        }
        Rule::ident => Ok(Value::Ident(inner.as_str().to_string())),
        _ => Err(format!("Unknown value type: {:?}", inner.as_rule())),
    }
}

fn parse_state_def(pair: pest::iterators::Pair<Rule>) -> Result<State, String> {
    let mut inner = pair.into_inner();

    let name = inner.next().ok_or("Expected state name")?.as_str();

    let mut state = State::new(name);

    for item in inner {
        match item.as_rule() {
            Rule::state_params => {
                for param in item.into_inner() {
                    if param.as_rule() == Rule::param_list {
                        for p in param.into_inner() {
                            if p.as_rule() == Rule::param {
                                let (key, value) = parse_property(p)?;
                                state.params.insert(key, value);
                            }
                        }
                    }
                }
            }
            Rule::state_body => {
                parse_state_body(item, &mut state)?;
            }
            _ => {}
        }
    }

    Ok(state)
}

fn parse_state_body(pair: pest::iterators::Pair<Rule>, state: &mut State) -> Result<(), String> {
    for item in pair.into_inner() {
        match item.as_rule() {
            Rule::property => {
                let (key, value) = parse_property(item)?;
                state.params.insert(key, value);
            }
            Rule::trigger_def => {
                let transition = parse_trigger_def(item)?;
                state.transitions.push(transition);
            }
            _ => {}
        }
    }

    Ok(())
}

fn parse_trigger_def(pair: pest::iterators::Pair<Rule>) -> Result<Transition, String> {
    let mut trigger_name = String::new();
    let mut trigger_params = Vec::new();
    let mut certainty = Certainty::Certain;
    let mut target_state = String::new();

    for item in pair.into_inner() {
        match item.as_rule() {
            Rule::trigger_expr => {
                // For now, just grab the first trigger (TODO: handle logic ops)
                for t in item.into_inner() {
                    if t.as_rule() == Rule::trigger {
                        let mut t_inner = t.into_inner();
                        if let Some(name) = t_inner.next() {
                            trigger_name = name.as_str().to_string();
                        }
                        if let Some(params) = t_inner.next() {
                            for p in params.into_inner() {
                                if let Ok(v) = parse_value(p) {
                                    trigger_params.push(v);
                                }
                            }
                        }
                    }
                }
            }
            Rule::certainty => {
                certainty = Certainty::from_glyph(item.as_str()).unwrap_or(Certainty::Certain);
            }
            Rule::ident => {
                target_state = item.as_str().to_string();
            }
            _ => {}
        }
    }

    Ok(Transition {
        trigger: if trigger_name.is_empty() {
            None
        } else {
            Some(Trigger {
                name: trigger_name,
                params: trigger_params,
            })
        },
        certainty,
        target_state,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_pet() {
        let input = r#"
            pet sleepy_cat {
                wander → sleep
                sleep → wander
            }
        "#;

        let result = parse_neko(input);
        assert!(result.is_ok(), "Parse failed: {:?}", result);

        let pet = result.unwrap();
        assert_eq!(pet.name, "sleepy_cat");
        assert!(pet.states.contains_key("wander"));
        assert!(pet.states.contains_key("sleep"));
    }

    #[test]
    fn test_state_with_params() {
        let input = r#"
            pet fast_cat {
                locomotion: quadruped
                
                wander(speed: 10, radius: 300px) {
                    on cursor_near → chase
                }
                
                chase(speed: 15) {
                    on timeout → wander
                }
            }
        "#;

        let result = parse_neko(input);
        assert!(result.is_ok(), "Parse failed: {:?}", result);

        let pet = result.unwrap();
        assert_eq!(pet.name, "fast_cat");
        assert_eq!(pet.locomotion, Locomotion::Quadruped);

        let wander = pet.states.get("wander").expect("wander state missing");
        assert!(wander.params.contains_key("speed"));
        assert!(wander.transitions.len() > 0);
    }

    #[test]
    fn test_certainty_in_transitions() {
        let input = r#"
            pet moody_cat {
                wander → ◕sleep
                sleep → ◔wander
            }
        "#;

        let result = parse_neko(input);
        assert!(result.is_ok(), "Parse failed: {:?}", result);

        let pet = result.unwrap();
        let wander = pet.states.get("wander").expect("wander state missing");
        assert_eq!(wander.transitions[0].certainty, Certainty::Likely);

        let sleep = pet.states.get("sleep").expect("sleep state missing");
        assert_eq!(sleep.transitions[0].certainty, Certainty::Unlikely);
    }

    #[test]
    fn test_certainty_glyphs() {
        assert_eq!(Certainty::Certain.probability(), 1.0);
        assert_eq!(Certainty::Likely.probability(), 0.75);
        assert_eq!(Certainty::Possible.probability(), 0.5);
        assert_eq!(Certainty::Unlikely.probability(), 0.25);
        assert_eq!(Certainty::Rare.probability(), 0.1);
    }

    #[test]
    fn test_easing_functions() {
        // Linear should be identity
        assert_eq!(Easing::Linear.apply(0.5), 0.5);

        // EaseIn should be slower at start
        assert!(Easing::EaseIn.apply(0.5) < 0.5);

        // EaseOut should be faster at start
        assert!(Easing::EaseOut.apply(0.5) > 0.5);

        // All should hit endpoints
        for easing in [
            Easing::Linear,
            Easing::EaseIn,
            Easing::EaseOut,
            Easing::EaseInOut,
        ] {
            assert_eq!(easing.apply(0.0), 0.0);
            assert!((easing.apply(1.0) - 1.0).abs() < 0.001);
        }
    }

    #[test]
    fn test_value_range() {
        let range = Value::Range(4.0, 8.0);
        for _ in 0..100 {
            let sampled = range.sample();
            assert!(sampled >= 4.0 && sampled <= 8.0);
        }
    }
}
