

### Requirmnet
* Ollama
* minstral-nemo 
* Tavily API Key
* UV

### Supports
Input: Photo and Videos
4 second video took 2 min to get output on a mac 4

### Options
options:

| Flag | Long Flag | Argument | Description |
|------|----------|----------|-------------|
| `-h` | `--help` | — | Show help message and exit |
| `-v` | `--verbose` | — | Enable console logging |
| `-f` | `--file_path` | `IMAGE` | Path to input image to analyze |
| `-at` | `--add_tavily_api` | `API Key` | Add Tavily API key (Only the first time)|

### How To run
```uv run main.py -v -f {Path To Photo/Video} -at {Tavily API KEY}```
#### Example:
```uv run main.py -v -f image/fridge.jpg -at tvly-dev-1234567890```

### Todo
* Give options to run with other ollama models
* Give options to use anthropic,chatgpt ect
* Make a config

