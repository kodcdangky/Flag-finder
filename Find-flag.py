from tkinter import *
from tkinter.ttk import Combobox
from PIL import Image, ImageTk
from io import BytesIO
import requests, json

root = Tk()
root.minsize(320, 21)
root.title('Flag Finder')
root.resizable(0, 0)

header = Frame(
    master=root,
    bg='light gray'
)
header.columnconfigure(0, weight=0)
header.columnconfigure(1, weight=1)
header.pack(fill='x', side='top')

body = Frame(
    master=root,
    bg='light gray'
)
body.pack(fill='x', side='top')

footer = Frame(
    master=root,
    bg='light gray'
)
footer.columnconfigure(0, weight=0)
footer.columnconfigure(1, weight=1)
footer.pack(fill='x', side='bottom')

lbl_country = Label(
    master=header,
    text='Choose a country:',
    bg='light gray'
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
    master=header,
    values=countries,
    state='readonly',
)
mnu_countries.grid(row=0, column=1, sticky='new', padx=5)


def show_flag(Event):
    try:
        footer.grid_slaves(column=0)[0].grid_forget()
        footer.grid_slaves(column=1)[0].grid_forget()
        body.pack_slaves()[0].pack_forget()
    except IndexError:
        pass

    try:
        img_width = str(1000)   # set flag width here, aspect ratio preserved
        link_json = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=pageimages&list=&titles=File:Flag of ' \
                    + mnu_countries.get() \
                    + '.svg&pithumbsize=' + img_width
        re = requests.get(link_json,
                          timeout=1,
                          headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
        re.raise_for_status()
        json_raw = re.json()
        json_id = json_raw['query']['pages']; json_id = json_id[tuple(json_id.keys())[0]]

        re = requests.get(json_id['thumbnail']['source'],
                          timeout=1,
                          headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
        re.raise_for_status()
        img = Image.open(BytesIO(re.content))
        img = img.resize((img.width * 8 // 10, img.height * 8 // 10), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        img_flag = Label(
            master=body,
            image=img,
            bg='light gray',
        )
        img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
        img_flag.pack()
    except requests.exceptions.Timeout:
        lbl_error_msg = Label(
            master=body,
            bg='light gray',
            text='Fetch request timed out. Please retry by reselecting the country.',
            justify='center'
        )
        lbl_error_msg.pack()
    except requests.exceptions.HTTPError:
        lbl_error_msg = Label(
            master=body,
            bg='light gray',
            text='HTTP Error. Code: ' + str(re.status_code) + '.\nMessage: ' + re.reason,
            justify='center'
        )
        lbl_error_msg.pack()


    lbl_credit = Label(
        master=footer,
        text='Photos fetched from the Wikimedia Commons in real time. Source: ',
        bg='light gray'
    )
    lbl_credit_link = Text(
        master=footer,
        bg='light gray',
        borderwidth=0,
        height=1,
        width=len('https://commons.wikimedia.org/wiki/File:' + json_id['pageimage']),
        font=('Segoe UI', 9)
    )
    lbl_credit_link.insert(0.0, 'https://commons.wikimedia.org/wiki/File:' + json_id['pageimage'])
    lbl_credit_link.configure(state='disabled')

    lbl_credit.grid(row=0, column=0, sticky='ws')
    lbl_credit_link.grid(row=0, column=1, sticky='ews', pady=1.5)

mnu_countries.bind('<<ComboboxSelected>>', show_flag)

root.mainloop()
