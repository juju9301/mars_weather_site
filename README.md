# Mars Weather Site

This is a Django-based web app I built to explore Playwright automation while incorporating some fun Mars-related data. 🚀

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Features
- 🌌 **Mars Weather Dashboard** – Displays the latest weather on Mars, fetched manually from REMS API (http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php).
- 📈 **Temperature Graphs** – Uses matplotlib to visualize min, max, and avg temperatures.
- 📝 **Basic Blog System** – Users can authenticate, compose posts, and attach a random Mars rover image to their entries.
- 🧪 **Automated Testing** – Pytest + Playwright tests, with reports generated via pytest-cov and pytest-html. Include basic tests, tests using overwritten request query parameters, overwritten response body, image text recognition
- 🔄 **CI/CD Integration** – Configured with CircleCI for automated testing.
- 🚀 **Live Deployment** – Hosted on PythonAnywhere (currently inactive due to becoming too large for free tier).

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/juju9301/mars_weather_site.git
    cd mars_weather_site
    ```
2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run the migrations:
    ```bash
    python manage.py migrate
    ```
5. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Usage
- **Mars Weather Dashboard**: Navigate to `/` to see the weather data for the latest sol available, as well as NASA's picture of the day and the posts submitted so far
- **Mars Weather Data**: Navigate to `/list` to see all the weather data available. Click [Update weather data] for latest weather data to get fetched and saved into the database
- **Temperature Graphs**: Access the temperature graphs at `/plot`. You can plot data for max, min and avg temperature. 
- **Blog System**: Authenticate and start creating blog posts at `/add_post`. You can fetch a random Mars picture taken by one of the three Mars rovers and attach it to the post. You can also leave comments for each post.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
