'''
Flag-finder 1.0.1a
A small program to fetch and display flag of selected country from Wikimedia's database
---------------------------------------------------------------------------------------

Uses:
- tkinter for GUI elements
- tkinter.ttk for Combobox (dropdown menu) GUI element which isn't available with base tkinter
- Pillow (PIL fork) for ImageTk to read png image and pass to tkinter Label since tkinter doesn't support png
- io for BytesIO to read image data
- requests to talk to Wikimedia's API

Design choice:
- Small, minimalistic
- Light gray background to help flags with color white at the border stands out
'''

from tkinter import *
from tkinter.ttk import Combobox
from PIL import ImageTk
from io import BytesIO
import requests

'''
Greeting window: a small, minimalistic window with a label 'Choose a country:' and a dropdown list of countries
for user to choose from
'''

root = Tk()
root.minsize(330, 0)
root.title('Flag Finder')
root.resizable(False, False)

header = Frame(
    master=root,
    background='light gray'
)
header.columnconfigure(0, weight=0)
header.columnconfigure(1, weight=1)
header.pack(fill='x', side='top')

body = Frame(
    master=root,
    background='light gray'
)
body.pack(fill='both', side='top')

footer = Frame(
    master=root,
    background='light gray'
)
footer.columnconfigure(0, weight=0)
footer.columnconfigure(1, weight=1)
footer.pack(fill='x', side='bottom')

lbl_country = Label(
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


def get_image(country):
    '''
    Attempts to fetch image of flag of selected country.
    Returns image of flag, and name of .svg image file (to be used in credits) if successful,
    or returns error message, and empty string as name of .svg file otherwise
    '''
    try:
        img_width = str(700)   # set flag width here, aspect ratio preserved
        link_json = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=pageimages&titles=File:Flag of ' \
                    + country \
                    + '.svg&pithumbsize=' + img_width
        re = requests.get(link_json,
                          timeout=1,
                          headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
        re.raise_for_status()

    except requests.exceptions.Timeout:
        lbl_error_msg = Label(
            master=body,
            background='light gray',
            text='JSON fetch request timed out. Please retry by reselecting the country.',
            justify='center'
        )
        return lbl_error_msg, ''

    except requests.exceptions.HTTPError:
        lbl_error_msg = Label(
            master=body,
            background='light gray',
            text='HTTP Error while fetching JSON. Code: ' + str(re.status_code) + '.\nMessage: ' + re.reason,
            justify='center'
        )
        return lbl_error_msg, ''


    try:
        '''
        json dict navigating. Format:
        {
          "batchcomplete": "",
          "query": {
            "pages": {
              str(pageid_number): {
                "pageid": pageid_number,
                "ns": 6,
                "title": "File:Flag of <country>.svg",
                "thumbnail": {
                  "source": <image link>,
                  "width": img_width,
                  "height": <depends on flag aspect ratio and img_width>
                },
                "pageimage": <image file name on Wikimedia>
              }
            }
          }
        }
        '''
        json_raw = re.json()
        json_id = json_raw['query']['pages'].popitem()[1]

        re = requests.get(json_id['thumbnail']['source'],
                          timeout=1,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
        re.raise_for_status()

        img = ImageTk.PhotoImage(file=BytesIO(re.content))
        img_flag = Label(
            master=body,
            image=img,
            background='light gray',
        )
        img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
        return img_flag, json_id['pageimage']

    except requests.exceptions.Timeout:
        lbl_error_msg = Label(
            master=body,
            background='light gray',
            text='Image fetch request timed out. Please retry by reselecting the country.',
            justify='center'
        )
        return lbl_error_msg, ''

    except requests.exceptions.HTTPError:
        lbl_error_msg = Label(
            master=body,
            background='light gray',
            text='HTTP Error while fetching image. Code: ' + str(re.status_code) + '.\nMessage: ' + re.reason,
            justify='center'
        )
        return lbl_error_msg, ''


def get_credit(file_flag):
    '''
    Returns credit, and a selectable link to .svg flag image file on Wikimedia
    if file_flag isn't empty (meaning get_image was successful),
    or returns two empty labels otherwise
    '''
    if file_flag == '':
        return Label(footer, background='light gray'), Label(footer, background='light gray')

    lbl_credit = Label(
        master=footer,
        text='Photos fetched from the Wikimedia Commons in real time. Source: ',
        background='light gray'
    )
    lbl_credit_link = Text(
        master=footer,
        background='light gray',
        borderwidth=0,
        height=1,
        width=len('https://commons.wikimedia.org/wiki/File:' + file_flag),
        font=('Segoe UI', 9)
    )
    lbl_credit_link.insert(0.0, 'https://commons.wikimedia.org/wiki/File:' + file_flag)
    lbl_credit_link.configure(state='disabled')
    return lbl_credit, lbl_credit_link


def show_flag(Event):
    '''
    First deletes existing credit and image (or error message) if exists,
    then insert new image (or error message) and new credits
    '''
    try:
        footer.grid_slaves(column=0)[0].grid_forget()
        footer.grid_slaves(column=1)[0].grid_forget()
        body.pack_slaves()[0].pack_forget()
    except IndexError:
        pass

    lbl_result, file_flag = get_image(mnu_countries.get())
    lbl_result.pack(fill='both')

    lbl_credit, lbl_credit_link = get_credit(file_flag)
    lbl_credit.grid(row=0, column=0, sticky='ws')
    lbl_credit_link.grid(row=0, column=1, sticky='ews', pady=1.5)


mnu_countries.bind('<<ComboboxSelected>>', show_flag)

root.mainloop()
