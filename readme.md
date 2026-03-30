# AI Chef 🍳

An automated culinary assistant that analyzes your ingredients (via photo or video) to suggest recipes using local LLMs and real-time web search.

---

### Prerequisites
* **Ollama**: For running local models.
* **Mistral-Nemo**: The default model used for analysis.
* **Tavily API Key**: Required for web-search capabilities.
* **UV**: Fast Python package management.

### Performance Notes
* **Hardware**: Tested on Mac M4.
* **Latency**: A 4-second video input currently processes in approximately 2 minutes.

---
### How it works
1. Takes the file(photo or video)
2. File is hashed and folder is created in temp/{file_hash}
3. Detect objects w/ **YOLO** 
4. Crops each object and save a copy in the hashed folder
5. Identify wach object w/ **llava** add to a list
6. List is formated
7. Pass list of ingrediants to **mistral-nemo** agent
8. Agent querys **tavily** for websearch

### Options & Flags

| Flag | Long Flag | Argument | Description |
| :--- | :--- | :--- | :--- |
| `-h` | `--help` | — | Show help message and exit |
| `-v` | `--verbose` | — | Enable console logging |
| `-f` | `--file_path` | `PATH` | Path to the input image or video to analyze |
| `-at` | `--add_tavily_api` | `KEY` | Add Tavily API key (Required for the first run) |

---

### How to Run


**First Time Setup:**
```bash
Run this once to configure your API key. The script will automatically generate a `.env` file for you.
```
**After, key is saved in temp/.env so no need for the -at flag**
```bash
uv run main.py -v -f image/fridge.jpg
```
