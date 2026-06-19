# fmx

A friendly CLI for Apple's **on-device Foundation Model** — `chat`, `respond`, and `schema`
from your terminal, on **macOS 26** today.

macOS 27 will ship a native `fm` command. `fmx` brings that same workflow to macOS 26 right
now, built on Apple's [`apple-fm-sdk`](https://github.com/apple/python-apple-fm-sdk). It uses
a distinct name (`fmx`) so it never collides with the future system `fm`.

```console
$ fmx chat
fmx chat — Apple on-device Foundation Model
Type a message, or /help for commands. /exit to quit.

you ❯ explain async/await in one sentence
fmx ❯ async/await lets you write non-blocking code that reads top-to-bottom, pausing at
       await points so other work can run while you wait on I/O.

you ❯ /save mychat.json
Saved 4 entries to mychat.json.
```

## Requirements

Everything runs **on-device** through Apple Intelligence — there's no cloud, no API key,
and it only works on a compatible Mac:

- **macOS 26 or later**
- **Apple silicon, M1 or later**, with **Apple Intelligence turned on**
  ([compatible devices](https://support.apple.com/en-us/121115))
- Python 3.10+

If the model isn't available, `fmx` tells you exactly why (Apple Intelligence off, device
ineligible, or model still downloading).

## Install

```bash
uv tool install fmx
# or
pipx install fmx
```

## Usage

### `fmx chat` — interactive

```bash
fmx chat
fmx chat -i "You are a terse shell expert."   # set system instructions
```

Slash commands inside a chat:

| Command | Description |
| --- | --- |
| `/help` | List commands |
| `/save <path>` | Save the conversation to JSON |
| `/load <path>` | Resume a saved conversation |
| `/clear` | Start fresh (keeps your instructions) |
| `/system <text>` | Replace instructions and start fresh |
| `/model` | Show model info |
| `/exit` | Quit (or Ctrl-D) |

### `fmx respond` — one-shot, scriptable

```bash
fmx respond "Summarize this in 5 words: <text>"
echo "say hi" | fmx respond -                       # prompt from stdin
fmx respond "Write a haiku about Swift" --stream     # stream tokens
fmx respond "Describe this" --image photo.jpg        # multimodal (repeatable)
fmx respond "Be terse." -t 0.2 --max-tokens 100      # temperature / token cap
```

### `fmx schema` — structured output

Build a JSON Schema, then constrain a response to it. Output is parseable JSON:

```bash
fmx schema object name:str age:int "bio:str:a short biography" tags:str[]

# pipe a schema straight into respond:
fmx schema object name:str age:int | fmx respond "Invent a person" --schema -
```

Field spec is `name:type[:description]`. Types: `str`, `int`, `float`, `bool` (append `[]`
for an array, e.g. `tags:str[]`).

## What about Private Cloud Compute / `/model`?

Not yet. `apple-fm-sdk` currently exposes **only** the on-device model — there's no Python
API for Private Cloud Compute. When Apple ships PCC access (via the SDK, or the native `fm`
in macOS 27), model switching will land behind `/model`; the code already isolates session
creation in `fmx/core.py` for exactly this.

## Roadmap

- [ ] `/model` → Private Cloud Compute, once the SDK exposes it
- [ ] Auto-defer to the native `fm` binary when running on macOS 27
- [ ] Homebrew formula
- [ ] Tool/function calling in `chat`

## Development

```bash
git clone https://github.com/manjunathshiva/fmx
cd fmx
uv sync
uv run fmx chat
uv run pytest          # model tests auto-skip if Apple Intelligence is unavailable
uv run ruff check .
```

## License

MIT. Built on Apple's `apple-fm-sdk` (Apache-2.0). Not affiliated with Apple.
