from tkinter import *
from tkinter.ttk import Combobox
from PIL import Image, ImageTk, UnidentifiedImageError
from io import BytesIO
import requests
from bs4 import BeautifulSoup

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
body.rowconfigure((0, 2), weight=1)
body.columnconfigure(0, weight=1)
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
        body.grid_slaves(row=0)[0].grid_forget()
        body.grid_slaves(row=1)[0].grid_forget()
        body.grid_slaves(row=2)[0].grid_forget()
    except IndexError:
        pass

    country = mnu_countries.get().split(' ')
    flag_file = 'Flag_of'
    for name in country:
        flag_file += '_' + name
    flag_file += '.svg'

    link_wiki = 'https://en.wikipedia.org/wiki/File:' + flag_file
    re = requests.get(link_wiki, timeout=1, headers={'User-Agent' : 'Mozilla/5.0 (nguyen6626nam@gmail.com) (Windows NT 10.0; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0'})
    re.raise_for_status()

    page = BeautifulSoup(re.content, 'lxml')
    for meta in page('meta'):
        if meta.get('property') == 'og:image':
            link_image = meta.get('content')
            break

    try:
        re = requests.get(link_image, timeout=1, headers={'User-Agent' : 'Mozilla/5.0 (nguyen6626nam@gmail.com) (Windows NT 10.0; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0'})
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
        img_flag.grid(rowspan=3, column=0, sticky='news')
    except requests.exceptions.HTTPError:
        lbl_error_msg0 = Label(
            master=body,
            bg='light gray',
            text='Failed to fetch the flag for this country. For now going to the image\'s source:',
            justify='center'
        )

        lbl_error_link = Text(
            master=body,
            bg='light gray',
            borderwidth=0,
            height=1,
            width=len(link_image),
            font=('Segoe UI', 9)
        )
        lbl_error_link.tag_config('center', justify=CENTER)
        lbl_error_link.insert(0.0, link_image, 'center')
        lbl_error_link.configure(state='disabled')

        lbl_error_msg1 = Label(
            master=body,
            bg='light gray',
            text='on your browser then reselecting the country fixes the problem (in most cases). Currently looking for a solution.',
            justify='center'
        )
        lbl_error_msg0.grid(row=0, column=0, sticky='n')
        lbl_error_link.grid(row=1, column=0)
        lbl_error_msg1.grid(row=2, column=0)


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
        width=len(link_wiki),
        font=('Segoe UI', 9)
    )
    lbl_credit_link.insert(0.0, link_wiki)
    lbl_credit_link.configure(state='disabled')

    lbl_credit.grid(row=0, column=0, sticky='ws')
    lbl_credit_link.grid(row=0, column=1, sticky='ews', pady=1.5)


mnu_countries.bind('<<ComboboxSelected>>', show_flag)

root.mainloop()
