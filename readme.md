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
uv run main.py -f image/fridge.jpg
```

## Example Output
**uv run main.py -f fridge-inside.JPG**
```
image 1/1 /Users/seascout/Programming/AI/Chef AI/fridge-inside.JPG: 608x640 3 bottles, 7 cups, 10 bowls, 1 apple, 1 vase, 36.4ms
Speed: 1.6ms preprocess, 36.4ms inference, 0.1ms postprocess per image at shape (1, 3, 608, 640)
Sure! Here are some recipes you can make with strawberries, radishes, peppers, cheese, milk, and mustard:

1. **Strawberry-Radish Salad with Creamy Lemon Dressing**
   - *Source:* https://www.forksoverknives.com/recipes/vegan-salads-sides/strawberry-radish-salad-with-creamy-lemon-dressing/
   - This refreshing springtime salad features spicy radishes, juicy strawberries, crisp cucumber, and a creamy lemon dressing. Get the recipe!

2. **Radish & Strawberry Salad**
   - *Source:* http://latavolamarcherecipebox.blogspot.com/2014/06/radish-strawberry-salad.html
   - In a bowl combine radishes, strawberry & onion. Season with salt & pepper and a light drizzle of olive oil. Very gently (with your hands) toss the salad to ...

3. **Strawberry Radish Salad Recipe**
   - *Source:* https://www.drmcdougall.com/education/nutrition/favorite-recipes-july-2006-celebrity-chef-weekend/
   - 1 Combine the strawberries, orange supremes, radishes, lemon juice, scallions and sugar. ... Season with salt and pepper. Arrange in a star pattern around the rim ...

4. **Oaxaca cheese, roasted radishes, and strawberries**
   - *Source:* https://www.reddit.com/r/foodbutforbabies/comments/15yd90w/oaxaca_cheese_roasted_radishes_and_strawberries/
   - I trimmed the ends and cut them in half, tossed in olive oil, black pepper, onion powder, garlic powder, and paprika and put on a baking sheet with the cut ...

5. **Recipe: Radish, Navy Bean and Pickled Strawberry Salad**
   - *Source:* https://westernliving.ca/food-and-wine/recipes/recipe-radish-navy-bean-and-pickled-strawberry-salad/
   - Recipe: Radish, Navy Bean and Pickled Strawberry Salad · 16 red radishes, divided · 1 tbsp grapeseed oil · Kosher salt and freshly ground black ...
Total time: 57.2137 seconds
```