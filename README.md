# Flag-finder
A small program to fetch flags of all countries from Wikimedia Commons database in real time

Known problems:
- "PIL.UnidentifiedImageError" on "img = Image.open(BytesIO(requests.get(link_image).content))" occasionally. Not sure if it's requests.get().content or BytesIO() fucking up, or if it's related to connection ((lack of) cert or something) since manually going to the link on browser then reselecting the country in the same session also fixes the problem ======> Solved by adding User-Agent to GET requests

Completed tasks:
- Now fetching image from Wikimedia API
