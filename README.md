# Tinct

A VS Code color theme where every color has a reason.

Most syntax themes assign colors arbitrarily — strings are green because someone liked green, keywords are purple because it looked nice next to the green. Tinct takes a different approach: **colors encode cognitive role**. Each hue maps to the function a token plays in your mental model of the program, so you can glance at a block of code and instantly understand its structure.

Designed for Python first, works well everywhere.

## The Color System

Tinct uses twelve chromatic zones, each mapped to a distinct cognitive role. Every token earns its color — nothing is gray by default.

| Color | Role | What it highlights |
|-------|------|-------------------|
| **Blue** | Structure | `def`, `class`, `lambda`, `import`, `from`, `as` |
| **Amber** | Flow | `if`, `for`, `while`, `return`, `try`, `except`, `raise`, `break`, `continue`, `pass`, `with` |
| **Green** | Values | strings, `True`, `False` |
| **Mint** | Numbers | numeric literals — cooler than strings to feel distinct |
| **Violet** | Logic | `and`, `or`, `not`, `is`, `in`, comparison operators |
| **Cyan** | Calls | function calls, built-in functions |
| **Coral** | Parameters | function parameters — the contract between caller and callee |
| **Teal** | Types | type hints, annotations — informational but semantically rich |
| **Pink** | Properties | attribute access (`self.x`, `obj.method`) |
| **Orange** | Decorators | `@property`, `@staticmethod` — they change behavior, they deserve attention |
| **Steel** | Self | `self`, `cls` — ever-present, deliberately quiet |
| **Sand** | Variables | local names — warm neutral, the connective tissue of code |

Three more elements complete the palette:

- **Olive** — docstrings, brighter than comments because they're documentation
- **Gray** — comments, punctuation, structural noise
- **Silver-blue** — `None`, representing absence/void rather than a concrete value


## Design Principles

1. **Colors encode role, not syntax category.** "Keyword" is not a useful category — `def` (structure) and `if` (flow) and `and` (logic) serve completely different cognitive functions and get completely different colors.

2. **Every token earns its color.** Nothing defaults to gray. Parameters, variables, types, properties, decorators, and `self` each get their own chromatic identity because they play distinct cognitive roles.

3. **Frequency inversely correlates with saturation.** Things you see constantly (variables, punctuation) use warm neutrals. Things that are rare and significant (literals, flow control) use vivid colors.

4. **`None` is void, not a value.** `True` and `False` are concrete values (green). `None` represents absence — it gets a muted silver-blue to visually separate it from affirmative data.

5. **Python-specific awareness.** `self` fades to steel. Decorators get warm orange because they change behavior. f-string interpolations are visually distinct from the string around them. Docstrings are brighter than comments because they're documentation, not notes.

## Variants

- **Tinct Dark** — deep navy background, optimized for extended coding sessions
- **Tinct Light** — warm white background, same philosophy adapted for daylight readability

## Installation

### From VS Code Marketplace
Search for "Tinct" in the Extensions panel, or:
```
ext install JoaquinCampo.tinct
```

### From VSIX
1. Download the `.vsix` file from [Releases](https://github.com/JoaquinCampo/tinct/releases)
2. In VS Code: Extensions panel → `...` menu → "Install from VSIX..."

### From Source
```bash
git clone https://github.com/JoaquinCampo/tinct.git
cd tinct
# Copy or symlink to your VS Code extensions directory:
# macOS/Linux: ~/.vscode/extensions/tinct
# Windows: %USERPROFILE%\.vscode\extensions\tinct
```

Then select the theme: Ctrl/Cmd+K Ctrl/Cmd+T → "Tinct Dark" or "Tinct Light"

## Best with Pylance

Tinct includes semantic token colors that work with VS Code's semantic highlighting (powered by Pylance for Python). This enables deeper distinctions — like coloring `self` differently from regular parameters, or distinguishing function definitions from function calls — that aren't possible with TextMate grammars alone.

Make sure `"editor.semanticHighlighting.enabled": true` in your settings (it's on by default).

