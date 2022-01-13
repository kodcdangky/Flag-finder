# Flag-finder
A small program to fetch flags of all countries from Wikimedia Commons database in real time

TODO:
- Write docs for the code file
- Fetch image from API or directly from the link to file
- Save a cache of flags each time program is started instead of fetching in real time to save time
- Make drop down box typable (ez) and live search while typing (WTFF)
- Turn .py into .exe

Known problems:
- "PIL.UnidentifiedImageError" on "img = Image.open(BytesIO(requests.get(link_image).content))" occasionally. Not sure if it's requests.get().content or BytesIO() fucking up, or if it's related to connection ((lack of) cert or something) since manually going to the link on browser then reselecting the country in the same session also fixes the problem ======> Solved by adding User-Agent to GET requests
