from flask import Flask, request, render_template
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
from datetime import datetime
from PIL import Image
import requests

load_dotenv()  # This loads the environment variables from .env

client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  
)

# set a directory to save DALL·E images to
image_dir_name = "static/img"
image_dir = os.path.join(os.curdir, image_dir_name)

# create the directory if it doesn't yet exist
if not os.path.isdir(image_dir):
    os.mkdir(image_dir)

# print the directory to save to
print(f"{image_dir=}")


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    max_retries = 5  # Maximum number of retries
    retry_delay = 1  # Initial delay between retries in seconds

    if request.method == 'POST':
        animal1 = request.form['animal1']
        animal2 = request.form['animal2']

        # Construct the prompt
        prompt = f"A silly, photorealistic image of a creature that's a blend of a {animal1} and a {animal2}."

        for attempt in range(max_retries):
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1024x1024",
                    quality="standard", # Alternatively, "hd"
                    response_format="url",
                    style="vivid", # Alternatively, "vivid"
                    n=1,
                )
                # If request is successful, break out of the retry loop
                break
            except Exception as e:
                print(f"Attempt {attempt+1} failed with error: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                if attempt == max_retries - 1:
                    # Return an error message if all retries fail
                    return render_template(
                        'error.html', 
                        error_message="Failed to process your request after several attempts." +\
                            "\nPlease try again later.")
        
        # Extract image URL
        print(response)
        # save the image
        formatted_date_time = datetime.now().strftime("%Y%m%d%H%M")
        generated_image_name = "img" + formatted_date_time + ".png" 
        generated_image_filepath = os.path.join(image_dir, generated_image_name)
        generated_image_url = response.data[0].url  # extract image URL from response
        generated_image = requests.get(generated_image_url).content  # download the image

        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(generated_image)  # write the image to the file
        return render_template('result.html', image_url=generated_image_filepath)

if __name__ == '__main__':
    app.run(debug=True)

# For example(s):
# https://github.com/openai/openai-cookbook/blob/main/examples/dalle/Image_generations_edits_and_variations_with_DALL-E.ipynb

# TODO: 
# Variations
# call the OpenAI API, using `create_variation` rather than `create`
# variation_response = client.images.create_variation(
#     image=generated_image,  # generated_image is the image generated above
#    n=2,
#    size="1024x1024",
#    response_format="url",
# )
