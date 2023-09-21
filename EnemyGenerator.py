import openai
import os.path
import sys
import json
import base64
from PIL import Image

os.chdir(os.path.dirname(os.path.realpath(__file__)))

def load_data(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path) as file:
        data = json.load(file)
    return data

def create_folder_and_write_stat(name, stat_block):
    enemies_folder_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Enemies")
    
    monster_folder_path = os.path.join(enemies_folder_path, name)
    
    os.makedirs(monster_folder_path, exist_ok=True)
    
    txt_file_path = os.path.join(monster_folder_path, f"{name}.txt")
    
    with open(txt_file_path, 'w') as file:
        file.write(stat_block)

def overlay_token_border(image_path, token_border_path, output_path):
    # Load the generated image
    image = Image.open(image_path)

    # Load the token border
    token_border = Image.open(token_border_path)

    # Overlay the token border onto the image
    combined_image = Image.alpha_composite(image.convert("RGBA"), token_border.convert("RGBA"))

    # Save the combined image to the specified output path
    combined_image.save(output_path)

API_Keys_data = load_data("API_Keys.json")
openai.api_key = API_Keys_data["AI_API_KEY"]

token_border_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Border256.png")

# Prompt the user for input
try:
    name = input("Enter a name for the monster: ")
    description = input("Enter a brief description for the monster: ")
    visual_description = input("Enter a basic visual description for the monster: ")
    CR = input("Enter a Combat Rating (CR) for the monster (Example: 5): ")
except Exception as e:
    sys.exit(f"Error: {str(e)}")

# Combine the inputs into a single prompt
prompt = f"Name: {name}\nDescription: {description}\nCombat Rating (CR): {CR}"

print("Generating stat block...")

# Call the chat model
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {
            "role": "system",
            "content": "You create monster stat blocks for the Dungeons & Dragons tabletop roleplaying game. The user prompts you with a name, a brief description and a combat rating. Using that information, you create an imaginative stat block to the best of your ability."
        },
        {"role": "user", "content": prompt }
    ],
    temperature=1.0,
    max_tokens=1500
)
    
stat_block = response['choices'][0]['message']['content']

create_folder_and_write_stat(name, stat_block)

print(f"\nStat block for {name} successfully written to Enemies/{name}/{name}.txt")
print("\nGenerating Sprites/Tokens...")

# Generate Sprites
response = openai.Image.create(
  prompt = f"{visual_description}, Portrait, Pixel art",
  n=3,
  size="256x256",
  response_format="b64_json"
)
image_data_b64 = response['data'][0]['b64_json']
image_data = base64.b64decode(image_data_b64)

# Create a directory path
image_dir = os.path.join(os.getcwd(), 'Images')
os.makedirs(image_dir, exist_ok=True)

# Loop over the returned images
for i, image_info in enumerate(response['data']):
    image_data_b64 = image_info['b64_json'] 
    image_data = base64.b64decode(image_data_b64)
    
    # Combine directory with the filename
    image_path = os.path.join(image_dir, f"{name}_{i+1}.png")

    # Save the image to the file
    with open(image_path, 'wb') as f:
        f.write(image_data)

    # Set the path for the output (edited) image with token border
    output_path = os.path.join(os.getcwd(), "Enemies", name, f"{name}_{i+1}.png")

    # Call the function to overlay the token border and save the edited image
    overlay_token_border(image_path, token_border_path, output_path)

print("\nSucessfully generated sprites/tokens")
print(f"\nTokens for {name} successfully saved to Enemies/{name}")