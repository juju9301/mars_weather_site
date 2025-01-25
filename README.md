a basic django site:
- showing the weather on Mars (data is being fetched manually via mars_weather_site\mars1\weather\fixtures\getdbfixture.py from http://cab.inta-csic.es/rems/wp-content/plugins/marsweather-widget/api.php)
- plotting the graph for min, max avg temperature with matplotlib
- basic auth with ability to compose posts and post it on home page. ability to fetch the random picture taken by one of the three Mars rovers and add it to post
- pytest + playwright tests, test reports with pytest-cov and pytest-html
- integrated with circle CI
- deployed at https://iancatface.pythonanywhere.com/ (not atm though)
