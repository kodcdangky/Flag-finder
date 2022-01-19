"""
Flag-finder 1.2.0
A small program to fetch and display flag of selected country from Wikimedia's database
---------------------------------------------------------------------------------------

Uses:
- tkinter for GUI elements
- tkinter.ttk for Combobox (dropdown menu) GUI element which isn't available with base tkinter

Design choice:
- Small, minimalistic
- Light gray background to help flags with color white at the border stands out
"""
from tkinter.ttk import Combobox
from PIL import ImageTk
from io import BytesIO
from hashlib import sha3_256
from time import time
from ast import literal_eval
import tkinter as tk
import requests, os


# Greeting window: a small window with a label 'Choose a country:' and a dropdown list of countries
# for user to choose from

root = tk.Tk()
root.minsize(330, 0)
root.title('Flag Finder')
root.resizable(False, False)

header = tk.Frame(
    master=root,
    background='light gray'
)
header.columnconfigure(0, weight=0)
header.columnconfigure(1, weight=1)
header.pack(fill='x', side='top')

body = tk.Frame(
    master=root,
    background='light gray'
)
body.pack(fill='both', side='top')

footer = tk.Frame(
    master=root,
    background='light gray'
)
footer.columnconfigure(0, weight=0)
footer.columnconfigure(1, weight=1)
footer.pack(fill='x', side='bottom')

lbl_country = tk.Label(
    master=header,
    text='Choose a country:',
    background='light gray'
)
lbl_country.grid(row=0, column=0, sticky='nw', padx=5)

countries = ('Afghanistan',
             'Albania',
             'Algeria',
             'Andorra',
             'Angola',
             'Antigua and Barbuda',
             'Argentina',
             'Armenia',
             'Australia',
             'Austria',
             'Azerbaijan',
             'Bahamas',
             'Bahrain',
             'Bangladesh',
             'Barbados',
             'Belarus',
             'Belgium',
             'Belize',
             'Benin',
             'Bhutan',
             'Bolivia',
             'Bosnia and Herzegovina',
             'Botswana',
             'Brazil',
             'Brunei',
             'Bulgaria',
             'Burkina Faso',
             'Burundi',
             'Cambodia',
             'Cameroon',
             'Canada',
             'Cape Verde',
             'Central African Republic',
             'Chad',
             'Chile',
             'China',
             'Colombia',
             'Comoros',
             'Democratic Republic of the Congo',
             'Republic of the Congo',
             'Costa Rica',
             'Croatia',
             'Cuba',
             'Cyprus',
             'Czech Republic',
             'Denmark',
             'Djibouti',
             'Dominica',
             'Dominican Republic',
             'East Timor',
             'Ecuador',
             'Egypt',
             'El Salvador',
             'Equatorial Guinea',
             'Eritrea',
             'Estonia',
             'Eswatini',
             'Ethiopia',
             'Fiji',
             'Finland',
             'France',
             'Gabon',
             'Gambia',
             'Georgia',
             'Germany',
             'Ghana',
             'Greece',
             'Grenada',
             'Guatemala',
             'Guinea',
             'Guinea-Bissau',
             'Guyana',
             'Haiti',
             'Honduras',
             'Hungary',
             'Iceland',
             'India',
             'Indonesia',
             'Iran',
             'Iraq',
             'Ireland',
             'Israel',
             'Italy',
             'Ivory Coast',
             'Jamaica',
             'Japan',
             'Jordan',
             'Kazakhstan',
             'Kenya',
             'Kiribati',
             'North Korea',
             'South Korea',
             'Kuwait',
             'Kyrgyzstan',
             'Laos',
             'Latvia',
             'Lebanon',
             'Lesotho',
             'Liberia',
             'Libya',
             'Liechtenstein',
             'Lithuania',
             'Luxembourg',
             'North Macedonia',
             'Madagascar',
             'Malawi',
             'Malaysia',
             'Maldives',
             'Mali',
             'Malta',
             'Marshall Islands',
             'Mauritania',
             'Mauritius',
             'Mexico',
             'Micronesia',
             'Moldova',
             'Monaco',
             'Mongolia',
             'Montenegro',
             'Morocco',
             'Mozambique',
             'Myanmar',
             'Namibia',
             'Nauru',
             'Nepal',
             'Netherlands',
             'New Zealand',
             'Nicaragua',
             'Niger',
             'Nigeria',
             'Norway',
             'Oman',
             'Pakistan',
             'Palau',
             'Palestine',
             'Panama',
             'Papua New Guinea',
             'Paraguay',
             'Peru',
             'Philippines',
             'Poland',
             'Portugal',
             'Qatar',
             'Romania',
             'Russia',
             'Rwanda',
             'Saint Kitts and Nevis',
             'Saint Lucia',
             'Saint Vincent and the Grenadines',
             'Samoa',
             'San Marino',
             'Sao Tome and Principe',
             'Saudi Arabia',
             'Senegal',
             'Serbia',
             'Seychelles',
             'Sierra Leone',
             'Singapore',
             'Slovakia',
             'Slovenia',
             'Solomon Islands',
             'Somalia',
             'South Africa',
             'South Sudan',
             'Spain',
             'Sri Lanka',
             'Sudan',
             'Suriname',
             'Sweden',
             'Switzerland',
             'Syria',
             'Taiwan',
             'Tajikistan',
             'Tanzania',
             'Thailand',
             'Togo',
             'Tonga',
             'Trinidad and Tobago',
             'Tunisia',
             'Turkey',
             'Turkmenistan',
             'Tuvalu',
             'Uganda',
             'Ukraine',
             'United Arab Emirates',
             'United Kingdom',
             'United States',
             'Uruguay',
             'Uzbekistan',
             'Vanuatu',
             'Vatican City',
             'Venezuela',
             'Vietnam',
             'Yemen',
             'Zambia',
             'Zimbabwe')
mnu_countries = Combobox(
    master=header,
    values=countries,
    state='readonly',
)
mnu_countries.grid(row=0, column=1, sticky='new', padx=5)


dir_flags_hash = f'{os.getenv("LocalAppData")}\\Flags'
os.makedirs(dir_flags_hash, exist_ok=True)
dir_flags = f'{os.getenv("AppData")}\\Flags'
os.makedirs(dir_flags, exist_ok=True)
def get_hash(file: str or bytes):
    """
    Returns SHA3-256 hex of a file, using either the file's path (for log file) or binary data (for image files)
    """

    if type(file) is str:
        with open(file, 'rb') as f:
            return sha3_256(f.read()).hexdigest()
    else:
        return sha3_256(file).hexdigest()


def cache_flag(country: str, img: bytes):
    """
    Store image of selected countries' flags, when they were cached, and hash of stored images in %AppData%\Roaming\Flags
    """

    # if log file not exists | log_hash not exists | hash of log file is not equal to log_hash data: make new log file
    if not os.path.exists(f'{dir_flags}\\log') or not os.path.exists(f'{dir_flags_hash}\\log_hash') \
            or get_hash(f'{dir_flags}\\log') != open(f'{dir_flags_hash}\\log_hash').read():
        with open(f'{dir_flags}\\log', 'w') as log:
            log.write('{}')

    with open(f'{dir_flags}\\log') as log:
        cache_log = literal_eval(log.read())

    with open(f'{dir_flags}\\{country}.png', 'wb') as image:
        image.write(img)

    cache_log[country] = (int(time()), get_hash(img))
    with open(f'{dir_flags}\\log', 'w') as log:
        log.write(str(cache_log))

    with open(f'{dir_flags_hash}\\log_hash', 'w') as log_hash:
        log_hash.write(get_hash(f'{dir_flags}\\log'))


def get_cache(country: str):
    """
    Returns path to image in cache if available and image is less than 1 week old,
    or returns False otherwise
    """

    # if .png of flag exists & log file exists & log_hash exists & hash of log file is equal to log_hash data: proceed
    if os.path.exists(f'{dir_flags}\\{country}.png') and os.path.exists(f'{dir_flags}\\log') and os.path.exists(f'{dir_flags_hash}\\log_hash') \
            and get_hash(f'{dir_flags}\\log') == open(f'{dir_flags_hash}\\log_hash').read():
        with open(f'{dir_flags}\\log') as file:
            log = literal_eval(file.read())
    else:
        return False

    # if country not in cache log | flag image older than 1 week | hash of image is not equal to recorded hash: no image
    cached = log.get(country, False)
    if not cached or int(time()) - cached[0] > 604800 or get_hash(f'{dir_flags}\\{country}.png') != cached[1]:
        return False

    with open(f'{dir_flags}\\{country}.png', 'rb') as file:
        return file.read()


def get_image(country: str):
    """
    Get image of flag of selected country from cache,
    if none found, fetch flag from Wikimedia and cache it.
    Returns image of flag, and name of .svg image file (to be used in credits) if successful,
    or returns error message, and empty string as name of .svg file otherwise
    """

    img = get_cache(country)
    if img:
        wiki_file = 'Flag_of'
        country_name = country.split(' ')
        for name in country_name:
            wiki_file += f'_{name}'
        wiki_file += '.svg'
    else:
        try:
            img_width = 700  # set display image of flag's width here, aspect ratio preserved
            param_api = {'action': 'query', 'format': 'json', 'prop': 'pageimages', 'titles': f'File:Flag of {country}.svg', 'pithumbsize': img_width}
            re = requests.get("https://commons.wikimedia.org/w/api.php",
                              timeout=1,
                              headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'},
                              params=param_api)
            re.raise_for_status()
    
        except requests.exceptions.Timeout:
            lbl_error_msg = tk.Label(
                master=body,
                background='light gray',
                text='JSON fetch request timed out. Please retry by reselecting the country.',
                justify='center'
            )
            return lbl_error_msg, ''
    
        except requests.exceptions.HTTPError:
            lbl_error_msg = tk.Label(
                master=body,
                background='light gray',
                text=f'HTTP Error while fetching JSON. Code: {re.status_code}.\nMessage: {re.reason}',
                justify='center'
            )
            return lbl_error_msg, ''
    
        try:
            # json dict navigating. Format:
            # {
            #   "batchcomplete": "",
            #   "query": {
            #     "pages": {
            #       str(pageid_number): {
            #         "pageid": pageid_number,
            #         "ns": 6,
            #         "title": "File:Flag of <country>.svg",
            #         "thumbnail": {
            #           "source": <image link>,
            #           "width": img_width,
            #           "height": <depends on flag aspect ratio and img_width>
            #         },
            #         "pageimage": <image file name on Wikimedia>
            #       }
            #     }
            #   }
            # }
            json = re.json()
            json = json['query']['pages'].popitem()[1]
    
            re = requests.get(json['thumbnail']['source'],
                              timeout=1,
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
            re.raise_for_status()
            img = re.content
            cache_flag(country, img)
            wiki_file = json['pageimage']
    
        except requests.exceptions.Timeout:
            lbl_error_msg = tk.Label(
                master=body,
                background='light gray',
                text='Image fetch request timed out. Please retry by reselecting the country.',
                justify='center'
            )
            return lbl_error_msg, ''
    
        except requests.exceptions.HTTPError:
            lbl_error_msg = tk.Label(
                master=body,
                background='light gray',
                text=f'HTTP Error while fetching image. Code: {re.status_code}.\nMessage: {re.reason}',
                justify='center'
            )
            return lbl_error_msg, ''

    img = ImageTk.PhotoImage(file=BytesIO(img))
    img_flag = tk.Label(
        master=body,
        image=img,
        background='light gray',
        )
    img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
    return img_flag, wiki_file


def get_credit(wiki_file: str):
    """
    Returns credit, and a selectable link to .svg flag image file on Wikimedia
    if wiki_file isn't empty (meaning get_image was successful),
    or returns two empty labels otherwise
    """

    if wiki_file == '':
        return tk.Label(footer, background='light gray'), tk.Label(footer, background='light gray')

    lbl_credit = tk.Label(
        master=footer,
        text='Photos courtesy of Wikimedia Commons. Source: ',
        background='light gray'
    )
    lbl_credit_link = tk.Entry(
        master=footer,
        readonlybackground='light gray',
        borderwidth=0,
        width=len(f'https://commons.wikimedia.org/wiki/File:{wiki_file}'),
        font=('Segoe UI', 9),
        justify='left'
    )
    lbl_credit_link.insert(0, f'https://commons.wikimedia.org/wiki/File:{wiki_file}')
    lbl_credit_link.configure(state='readonly')
    return lbl_credit, lbl_credit_link


def show_flag(_):
    """
    First deletes existing credit and image (or error message) if exists,
    then insert new image (or error message) and new credits
    """

    try:
        footer.grid_slaves(column=0)[0].grid_forget()
        footer.grid_slaves(column=1)[0].grid_forget()
        body.pack_slaves()[0].pack_forget()
    except IndexError:
        pass

    lbl_result, wiki_file = get_image(mnu_countries.get())
    lbl_result.pack(fill='both')

    lbl_credit, lbl_credit_link = get_credit(wiki_file)
    lbl_credit.grid(row=0, column=0, sticky='ws', padx=(5, 0))
    lbl_credit_link.grid(row=0, column=1, sticky='ews', pady=1)


mnu_countries.bind('<<ComboboxSelected>>', show_flag)

root.mainloop()
