from tkinter import *
from tkinter.ttk import Combobox

import PIL
from PIL import Image, ImageTk
from io import BytesIO
import requests
from bs4 import BeautifulSoup

root = Tk()
root.minsize(320, 21)
root.title('Flag Finder')
root.resizable(0, 0)

window = Frame()
window.pack(fill='both')
window.rowconfigure((0, 2), weight=1, minsize=21)
window.columnconfigure(0, weight=0)
window.columnconfigure(1, weight=1)

lbl_country = Label(
    master=window,
    text='Choose a country:',
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
             # 'Kosovo',
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
             'Saint Kitts & Nevis',
             'Saint Lucia',
             'Saint Vincent and the Grenadines',
             'Samoa',
             'San Marino',
             'Sao Tome & Principe',
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
    master=window,
    values=countries,
    state='readonly',
)
mnu_countries.grid(row=0, column=1, sticky='new', padx= 5)

def fetch_flag(country):
    country = country.split(' ')
    flag_file = 'Flag_of'
    for name in country:
        flag_file += '_' + name
    flag_file += '.svg'

    link_wiki = 'https://en.wikipedia.org/wiki/File:' + flag_file
    re = requests.get(link_wiki, timeout= 1)
    if re.status_code != requests.codes.ok:
        raise re.raise_for_status()

    page = BeautifulSoup(re.content, 'lxml')
    for meta in page('meta'):
        if meta.get('property') == 'og:image':
            link_image = meta.get('content')
            break

    try:
        img = Image.open(BytesIO(requests.get(link_image).content))
        img = img.resize((img.width // 2, img.height // 2), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        img_flag = Label(
            master=window,
            image=img
        )
        img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
        return img_flag, link_wiki
    except PIL.UnidentifiedImageError:
        lbl_fetch_error = Label(
            master=window,
            text='Failed to fetch the flag for this country. For now restarting the program fixes the problem.\nCurrently looking for a solution.',
            justify='center'
        )
        return lbl_fetch_error, link_wiki

def show_flag(Event):
    try:
        try:
            window.grid_slaves(row=1)[0].grid_forget()
            window.grid_slaves(row=2)[0].grid_forget()
        except IndexError:
            pass

        lbl_display, link_wiki = fetch_flag(mnu_countries.get())
        lbl_display.grid(row=1, columnspan=2, sticky='news')

        lbl_credit = Label(
            master=window,
            text='Photos fetched from the Wikimedia Commons in real time. Source: ' + link_wiki
        )
        lbl_credit.grid(row=2, columnspan=2, sticky='news')

    except FileNotFoundError:
        try:
            window.grid_slaves(row=1)[0].grid_forget()
            window.grid_slaves(row=2)[0].grid_forget()

        except IndexError:
            pass

mnu_countries.bind('<<ComboboxSelected>>', show_flag)

root.mainloop()
