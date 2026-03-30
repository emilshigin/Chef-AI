import time

import cv2,os,sys,argparse
import base64
from typing import Dict, Any
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from dotenv import set_key

# AI imports
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import tool
from ultralytics import YOLO
from tavily import TavilyClient

# Global_var
tavily_api_key = None

# Utils 
def prRed(s): print("\033[91m{}\033[00m".format(s)) 
def prGreen(s): print("\033[92m{}\033[00m".format(s)) 
def prYellow(s): print("\033[93m{}\033[00m".format(s))
def prLightPurple(s): print("\033[94m{}\033[00m".format(s)) 
def prCyan(s): print("\033[96m{}\033[00m".format(s)) 

# AI Tools 
def load_api_key()->bool: 
    env_path = Path("temp")/".env"
    load_dotenv(dotenv_path=env_path)
    global tavily_api_key
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    return tavily_api_key is not None and tavily_api_key != ""

def save_api_key_to_temp(api_key):
    temp_dir = Path("temp")
    env_file = temp_dir / ".env"
    
    # Ensure directory exists (safe even if already created)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Create .env file
    env_file.touch(mode=0o600, exist_ok=True)

    # Write key
    set_key(env_file, "TAVILY_API_KEY", api_key)
    prGreen("Added Tavily API Key")


@tool
def web_search_with_key(query: str) -> Dict[str, Any]:
    """Search the web using Tavily API"""
    return web_search(query, api_key=tavily_api_key)


def web_search( query: str, api_key: str) -> Dict[str, Any]:
    if verbose:
        print("Func:web_search,\nVAR: query:",query)
    tavily_client = TavilyClient(api_key=api_key)
    return tavily_client.search(query)



def parse_args():
    # Global verbose flag
    global verbose
    parser = argparse.ArgumentParser(
        prog="\033[95mrecipe_finder_AI\033[00m",
        description="Input photo of fridge and pantry, get recommendations for recipes"
        )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="Include Console Logs"
    )

    parser.add_argument(
        "-f","--file_path", 
        metavar="IMAGE",
        type=str,
        help="Input image to analyse"
        )
    
    parser.add_argument(
        "-at","--add_tavily_api",
        metavar="API Key",
        help="Add tavily API Key "
    )

    args = parser.parse_args()
    verbose = args.verbose
    return args

# threashold 5 - 21 skipped
# threashold 20 - 79 skipped 
# grayscale it - 80 skipped


def is_similar(frame1, frame2, threshold=30):
    f1 = cv2.cvtColor(cv2.resize(frame1, (64,64)), cv2.COLOR_BGR2GRAY)
    f2 = cv2.cvtColor(cv2.resize(frame2, (64,64)), cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(f1, f2)
    return diff.mean() < threshold

def crop_found_objects(file_path, results):
    with open(file_path, "rb") as f:
            file_check_sum = hashlib.md5(f.read()).hexdigest()
    crop_dir = Path("temp") / file_check_sum
    crop_dir.mkdir(parents=True, exist_ok=True)

    crops = []
    prev_frame = None
    stat_frames_skipped = 0

    # Check if video
    is_video = file_path.lower().endswith(('.mp4', '.avi', '.mov'))

    if is_video:
        for frame_idx, r in enumerate(results):
            img = r.orig_img  # YOLO streaming frame

            if img is None:
                continue

            frame_interval = 5  # only check every 2nd frame
            if frame_idx % frame_interval != 0:
                stat_frames_skipped += 1
                continue

            # Skip very similar frames
            if prev_frame is not None and is_similar(prev_frame, img):
                stat_frames_skipped += 1
                continue

            prev_frame = img

            # Skip if no detections
            if r.boxes is None or len(r.boxes) == 0:
                continue

            for i, box in enumerate(r.boxes.xyxy.tolist()):
                x1, y1, x2, y2 = map(int, box)
                crop = img[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                crops.append(crop)
                cv2.imwrite(f"{crop_dir}/frame_{frame_idx}_item_{i}.jpg", crop)

        if verbose:
            prCyan(f"Frames skipped due to similarity: {stat_frames_skipped}")

    else:
        # Single image
        img = cv2.imread(file_path)
        r = results[0]
        if r.boxes is not None and len(r.boxes) > 0:
            for i, box in enumerate(r.boxes.xyxy.tolist()):
                x1, y1, x2, y2 = map(int, box)
                crop = img[y1:y2, x1:x2]
                crops.append(crop)
                cv2.imwrite(f"{crop_dir}/item_{i}.jpg", crop)

    return crops

def encode_image(img_array):
    _, buffer = cv2.imencode(".jpg", img_array)
    return base64.b64encode(buffer).decode("utf-8")


def identify_crop_objects(crops,agent, history):
    identified_items = []

    seen_crop_hashes = set()
    for crop in crops:
        h = hashlib.md5(cv2.resize(crop, (32,32)).tobytes()).hexdigest()

        if h in seen_crop_hashes:
            if verbose:
                print("skipped cropped frame")
            continue

        seen_crop_hashes.add(h)

        img_b64 = encode_image(crop)
        data_url = f"data:image/jpeg;base64,{img_b64}"

        message = HumanMessage(content=[
            {"type": "text", "text": "What food item is this?"},
            {
                "type": "image_url",
                "image_url": {"url": data_url}
            }
        ])

        response = agent.invoke({"messages": example_history +[message]})
        item = response["messages"][-1].content
        
        identified_items.append(item)
    return identified_items

def format_identify_objects(identified_items):
    cleaned_items = []
    if verbose:
        prLightPurple("Identified Grocieres:")

    for item in identified_items:
        item = item.lower().strip()

        # remove long sentences
        if len(item.split()) > 7:
            continue
        
        if "unknown" in item:
            continue
        if item in cleaned_items:
            continue

        cleaned_items.append(item)

        if verbose:
            print(item)

    # remove duplicates
    return list(set(cleaned_items))

def llava_agent_create():
    agent = create_agent(
        model=init_chat_model(
            model="llava", 
            model_provider="ollama",
              temperature=0
        ),
        system_prompt="""
        You are identifying food items from images.
        Return only the food name.

        Rules:
        - One item only
        - No punctuation
        - No sentences
        - No explanation
        - If unsure return: unknown


        Examples:
        milk
        mustard
        yogurt
        unknown
        """
        )
    example_history = [
        HumanMessage(content="What food item is this?"),
        AIMessage(content="apple"),
        HumanMessage(content="What food item is this?"),
        AIMessage(content="mustard"),
        HumanMessage(content="What food item is this?"),
        AIMessage(content="carton of eggs"),
        HumanMessage(content="What food item is this?"),
        AIMessage(content="unknown"),
    ]
    return {
        "agent": agent,
        "history": example_history
        }

def base_agent_create():
    return create_agent(
        model=init_chat_model(model="mistral-nemo",model_provider="ollama"),
        tools=[web_search_with_key],
        system_prompt = """
        You are a personal chef. The user will give you a list of ingredients they have left over in their house.
        Using the web search tool, search the web for recipes that can be made with the ingredients they have.
        Return recipe suggestions and eventually the recipe instructions to the user, if requested.
        """,
        checkpointer=InMemorySaver()
    )


def main():
    start = time.perf_counter()
    # Check Args
    args = parse_args()
    if not args.file_path:
        prRed("Error: No file linked or file does not exist")
        return 1
    
    if args.add_tavily_api:
        save_api_key_to_temp(args.add_tavily_api)


    if not load_api_key():
        prRed("Error: API key Not found\nRun flag -at add the Tavily API Key (only the first time)")
        return 1
    
    llava_config = llava_agent_create()
    llava_agent = llava_config["agent"]
    llava_history = llava_config["history"]

    # Object Detection AI
    if verbose:
        prLightPurple("Set up model")
    yolo_model = YOLO("yolo26n.pt")
    results = yolo_model(args.file_path, stream=True, conf=0.3)

    if verbose:
        prLightPurple("Crop Model")
    crops = crop_found_objects(args.file_path,results)
    if verbose:
        prLightPurple("Identifing Items")
    identified_items = identify_crop_objects(crops)
    if verbose:
        prLightPurple("Formating")
    ingredient_list = format_identify_objects(identified_items)

    # Web Search w/ Tavily
    if verbose:
        prLightPurple("Seating up and searching the web")

    base_agent = base_agent_create()

    response = base_agent.invoke(
        {"messages": [HumanMessage(content=f"I have some {ingredient_list}. What can I make?")]},
        config
    )

    print(response['messages'][-1].content)
    end = time.perf_counter()
    print(f"Total time: {end - start:.4f} seconds")
    return 0


if __name__ == "__main__":
    sys.exit(main())
