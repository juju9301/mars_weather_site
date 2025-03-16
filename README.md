# Mars Weather Site

This is a Django-based web app I built to explore Playwright automation while incorporating some fun Mars-related data. 🚀

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features
- 🌌 **Mars Weather Dashboard** – Displays the latest weather on Mars, fetched manually from REMS API (http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php).
- 📈 **Temperature Graphs** – Uses matplotlib to visualize min, max, and avg temperatures.
- 📝 **Basic Blog System** – Users can authenticate, compose posts, and attach a random Mars rover image to their entries.
- 🧪 **Automated Testing** – pytest + playwright tests, with reports generated via pytest-cov and pytest-html.
- 🔄 **CI/CD Integration** – Configured with CircleCI for automated testing and deployment.
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
- **Mars Weather Dashboard**: Navigate to `/weather` to view the latest Mars weather.
- **Temperature Graphs**: Access the temperature graphs at `/temperatures`.
- **Blog System**: Authenticate and start creating blog posts at `/blog`.

## Contributing
Contributions are welcome! Please follow these steps to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
