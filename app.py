from flask import Flask, request, render_template, url_for
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
    image_dir_path = os.path.join('static', 'img')  # Full path to the image directory
    image_files = [file for file in os.listdir(image_dir_path) if file.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Sort files by modification time in descending order (newest first)
    image_files.sort(key=lambda file: os.path.getmtime(os.path.join(image_dir_path, file)), reverse=True)
    
    # Generate URLs for the sorted image files
    image_urls = [url_for('static', filename=os.path.join('img', file).replace(os.sep, '/')) for file in image_files]
    return render_template('index.html', image_urls=image_urls)

@app.route('/generate', methods=['POST'])
def generate():
    max_retries = 5  # Maximum number of retries
    retry_delay = 1  # Initial delay between retries in seconds

    if request.method == 'POST':
        print(request.form)
        animal1 = request.form['animal1']
        animal2 = request.form['animal2']
        
        # Construct the prompt
        prompt = "Create a silly, photorealistic image of a creature with " +\
            f"the body of a {animal1}, and the attributes and features of a {animal2}." +\
            "No text."
        print(prompt)

        for attempt in range(max_retries):
            try:
                print("Generating [1/2]")
                response_1 = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1792x1024",
                    quality="standard", # Alternatively, "hd"
                    response_format="url",
                    style="vivid", # Alternatively, "vivid"
                    n=1,
                )
                print("Generating [2/2]")
                response_2 = client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size="1792x1024",
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
    
        try:
            # Save the images and generate file paths
            image_filepaths = []
            formatted_date_time = datetime.now().strftime("%Y%m%d%H%M")
            for i in [1,2]:
                if i == 1:
                    print("Saving image [1/2]")
                    response = response_1
                else:
                    print("Saving image [2/2]")
                    response = response_2
                generated_image_name = f"img_{i}_{formatted_date_time}.png" 
                generated_image_filepath = os.path.join(image_dir, generated_image_name)
                generated_image_url = response.data[0].url  # extract image URL from response
                generated_image = requests.get(generated_image_url).content  # download the image

                with open(generated_image_filepath, "wb") as image_file:
                    image_file.write(generated_image)  # write the image to the file
                image_filepaths.append(generated_image_filepath)

            # Pass both image file paths to the template
            return render_template('result.html', image_urls=image_filepaths)
        except Exception as e:
            print(f"Saving image(s) failed with error: {str(e)}")
            # Return an error message if all retries fail
            return render_template(
                'error.html', 
                error_message="Failed to process your request. Please try again.")
if __name__ == '__main__':
    app.run(debug=True)


