from flask import Flask, render_template_string, request, redirect, url_for
import json
import httpx
import base64

app = Flask(__name__)

# Initialize the HTTP client with headers
client = httpx.Client(
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

# Function to scrape Instagram user data
def scrape_user(username: str):
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    user_data = data["data"]["user"]

    # Fetch profile picture and encode it in Base64
    profile_pic_url = user_data["profile_pic_url_hd"]
    response = client.get(profile_pic_url)
    profile_pic_base64 = base64.b64encode(response.content).decode('utf-8')
    
    # Add Base64-encoded image to user_data
    user_data["profile_pic_base64"] = profile_pic_base64
    return user_data

# Redirect from root to /profile with default username
@app.route('/')
def home():
    return redirect(url_for('profile', username="emineey41"))

# Flask route to display user profile information
@app.route('/profile')
def profile():
    # Get the username from the query parameters
    username = request.args.get('username', "emineey41")
    user_data = scrape_user(username)

    # Define an HTML template for rendering the user data
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ user_data['username'] }}'s Profile</title>
    </head>
    <body>
        <h1>Instagram Profile of {{ user_data['username'] }}</h1>
        <img src="data:image/jpeg;base64,{{ user_data['profile_pic_base64'] }}" alt="Profile Picture" >
        <p><strong>Username:</strong> {{ user_data['username'] }}</p>
        <p><strong>Full Name:</strong> {{ user_data['full_name'] }}</p>
        <p><strong>Followesrs:</strong> {{ user_data['edge_followed_by']['count'] }}</p>
        <p><strong>Following:</strong> {{ user_data['edge_follow']['count'] }}</p>
        <p><strong>Biography:</strong> {{ user_data['biography'] }}</p>
    </body>
    </html>
    """
    
    # Render the HTML with the user's data
    return render_template_string(html_template, user_data=user_data)

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
