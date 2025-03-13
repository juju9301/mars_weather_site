import easyocr

reader = easyocr.Reader(['en'])
info = reader.readtext(r'C:\\Users\\Ivan\\Documents\\py_projects\\mars_weather_site\\mars1\\tests\\e2e\\plotscr.png')

for el in info:
    print(el)