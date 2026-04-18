# logsnip

> CLI tool to extract and filter structured log chunks from large files by time range or pattern

---

## Installation

```bash
pip install logsnip
```

Or install from source:

```bash
git clone https://github.com/yourname/logsnip.git && cd logsnip && pip install .
```

---

## Usage

```bash
# Extract logs between two timestamps
logsnip extract app.log --from "2024-01-15 08:00:00" --to "2024-01-15 09:00:00"

# Filter by pattern
logsnip extract app.log --pattern "ERROR|CRITICAL"

# Combine time range and pattern, output to file
logsnip extract app.log --from "2024-01-15 08:00:00" --to "2024-01-15 09:00:00" \
  --pattern "ERROR" --output errors.log

# Show help
logsnip --help
```

### Options

| Flag | Description |
|------|-------------|
| `--from` | Start of time range (inclusive) |
| `--to` | End of time range (inclusive) |
| `--pattern` | Regex pattern to match log lines |
| `--output` | Write results to a file instead of stdout |
| `--format` | Log timestamp format (default: `%Y-%m-%d %H:%M:%S`) |

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).