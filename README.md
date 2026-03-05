# Tinct

A VS Code color theme where every color has a reason.

Most syntax themes assign colors arbitrarily — strings are green because someone liked green, keywords are purple because it looked nice next to the green. Tinct takes a different approach: **colors encode cognitive role**. Each hue maps to the function a token plays in your mental model of the program, so you can glance at a block of code and instantly understand its structure.

Designed for Python first, works well everywhere.

## The Color System

Tinct uses six hues, each assigned to a specific cognitive role:

| Color | Role | What it highlights | Why this color |
|-------|------|-------------------|----------------|
| **Blue** | Structure | `def`, `class`, `lambda`, `import`, `from`, `as` | Blueprints and architecture — blue is stability, the skeleton of your program |
| **Amber** | Flow | `if`, `for`, `while`, `return`, `yield`, `try`, `except`, `raise`, `break`, `continue`, `pass`, `with`, `assert` | Traffic lights and caution — amber says "pay attention, execution could go different ways" |
| **Green** | Values | strings, numbers, `True`, `False`, `None` | Ground truth — green is concrete reality, the raw data your program operates on |
| **Purple** | Logic | `and`, `or`, `not`, `is`, `in`, comparison operators | Reasoning and thought — purple marks the decision-making layer |
| **Cyan** | References | function calls, built-in functions and types | Between structure (blue) and values (green) — references are how you *use* structure to *access* values |
| **Gray** | Meta | comments, docstrings, type hints, decorators, `self`/`cls`, punctuation | Not executed, not competing — informational elements fade so executable code stands out |

### Subcategories within each role

Colors vary in lightness and saturation within each hue family to distinguish subcategories:

**Structure (Blue)**
- `def`, `class`, `lambda` — full blue, these are the primary structural keywords
- Function/class names at definition — slightly lighter, the name being defined
- `import`/`from`/`as` — slightly darker, import is structural but secondary

**Flow (Amber)**
- `if`/`for`/`while`/`with` — full amber, primary control flow
- `return`/`yield` — lighter amber, these are exit points
- `try`/`except`/`raise` — darker amber, exceptional paths deserve gravity
- `break`/`continue`/`pass` — muted amber, minor flow adjustments

**Values (Green)**
- Strings — warm green, textual data
- Numbers — teal-green (cooler), numeric data feels different from text
- `True`/`False`/`None` — bold green, special sentinel values
- f-string expressions — amber braces (they're dynamic, flow-like)

**Logic (Purple)**
- `and`/`or`/`not` — full purple, boolean logic
- `is`/`in`/comparisons — same purple, same cognitive role
- Math operators — desaturated purple-gray, too common to be vivid
- Assignment `=` — nearly neutral, just plumbing

**References (Cyan)**
- Function calls — full cyan, where action happens
- Built-in functions/types — slightly brighter cyan, standard library

**Meta (Gray)**
- Comments — dim, background information
- Docstrings — slightly brighter than comments, they have lasting value
- Type hints — between comments and code, informational
- Decorators — warm peach (not gray), because decorators *change behavior*
- `self`/`cls` — dim, you always know they're there
- Punctuation — very dim, structural noise

## Design Principles

1. **Colors encode role, not syntax category.** "Keyword" is not a useful category — `def` (structure) and `if` (flow) and `and` (logic) serve completely different cognitive functions and get completely different colors.

2. **Frequency inversely correlates with saturation.** Things you see constantly (variables, punctuation) stay neutral. Things that are rare and significant (literals, flow control) use vivid colors.

3. **Related concepts share hue families.** All literal values are green-family. All structural definitions are blue-family. You should be able to identify the *category* of any token from its color alone.

4. **Python-specific awareness.** `self` fades to near-invisible. Decorators get their own warm treatment because they genuinely affect behavior. f-string interpolations are visually distinct from the string around them. Docstrings are brighter than comments because they're documentation, not notes.

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

## License

MIT
