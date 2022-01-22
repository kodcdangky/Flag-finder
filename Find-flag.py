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

from PIL import ImageTk
from io import BytesIO
from hashlib import sha3_256
from time import time
from ast import literal_eval
from fnmatch import fnmatch
from string import ascii_lowercase
import tkinter as tk
import tkinter.ttk as ttk
import requests, os

# Greeting window: a small window with a label and a dropdown list of countries for user to choose from

class SearchableCombobox(ttk.Combobox):
    """
    A ttk.Combobox whose entry field comes with autocompletion and can be used as a search bar
    """

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(state='normal')
        self.focus_set()
        self.bind('<KeyRelease>', self.autocomplete)
        self.bind('<<ComboboxSelected>>', self.handle_cbox_selected)
        self.bind('<Return>', self.handle_cbox_selected)
        self.bind('<FocusIn>', lambda _: self.selection_range(0, 'end'))
        
    def handle_cbox_selected(self, _) -> None:
        """
        Changes Combobox's dropdown depending on what is typed in by user.
        Shows the dropdown list with elements with the letters typed in, in the corresponding order,
        or if an element was typed correctly/selected, show its result
        """

        if not ''.join(self.get().split(' ')).isalpha():
            return

        if self.get() not in self['values']:
            elem_list = tuple(self['values'])
            self.configure(postcommand=lambda: None)
            matching_elem = []

            for elem in elem_list:
                if len(self.get()) > len(elem): continue

                last_checked = -1
                for typed_char in self.get().lower():
                    for index, char in enumerate(elem[last_checked + 1:].lower()):
                        if typed_char == char:
                            last_checked += index + 1
                            break
                    else:
                        break
                else:
                    matching_elem.append(elem)

            if len(matching_elem) == 0:
                matching_elem = list(elem_list)
                matching_elem.insert(0, '--------------------')
                matching_elem.insert(0, '<No match found, try a different pattern or select from the list below>')
                self.configure(width=len('<No match found, try a different pattern or select from the list below>'))

            self.configure(values=matching_elem)
            self.event_generate('<Down>')
            self.configure(postcommand=lambda: self.configure(values=elem_list))

        else:
            show_flag()

    def autocomplete(self, event) -> None:
        """
        Automatically completes the combobox entry field with the first element's name found that matches exactly with what
        has been typed in so far, continuously update the autocompletion as user continues typing
        """

        typed = self.get()
        elem_list = tuple(self['values'])
        # <event.state> = 8 -> No modifiers (irrelevant)
        #               = 9 -> Shift (irrelevant)
        #               = 12 -> Ctrl
        #               = 13 -> Ctrl+Shift
        #               = 131080 -> Alt
        #               = 131081 -> Alt+Shift
        #               = 131084 -> Ctrl+Alt
        #               = 131085 -> Ctrl+Alt+Shift
        #               = ... -> To be discovered
        if not ''.join(typed.split(' ')).isalpha() or typed in elem_list \
                or event.state in (12, 13, 131080, 131081, 131084, 131085) \
                or event.keysym.lower() not in tuple(ascii_lowercase):
            return

        for elem in elem_list:
            if len(typed) > len(elem):
                continue

            if fnmatch(elem.lower(), f'{typed}*'):
                self.set(elem)
                self.selection_range(len(typed), 'end')
                self.icursor('end')
                break


class ToolTip():
    """
    An appear-on-hover-at-mouse-location tooltip. Works with a tkinter widget master
    """
    def __init__(self, master=None, text=''):
        self.master = master
        self.text = text
        self.tip_window = None
        self.master.bind('<Enter>', self.showtip)
        self.master.bind('<Leave>', self.hidetip)

    def showtip(self, _):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return

        self.tip_window = tk.Toplevel(self.master)

        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f'+{self.master.winfo_pointerx()}+{self.master.winfo_pointery()}')

        label = tk.Label(master=self.tip_window,
                         text=self.text,
                         justify='left',
                         background='#ffffe0',
                         relief='solid',
                         borderwidth=1,
                         font=('Segoe UI', '9'))
        label.pack(ipadx=2)

    def hidetip(self, _):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()


root = tk.Tk()
root.minsize(400, 0)
root.title('Flag Finder')
root.resizable(False, False)

ttk.Style().configure('TFrame', background='light gray')

ttk.Style().configure('TLabel', background='light gray')
ttk.Style().configure('Error.TLabel', anchor='center', justify='center')

header = ttk.Frame(root)
header.columnconfigure(0, weight=0)
header.columnconfigure(1, weight=1)
header.pack(fill='x')

body = ttk.Frame(root)
body.pack(fill='both')

footer = ttk.Frame(root)
footer.columnconfigure(0, weight=0)
footer.columnconfigure(1, weight=1)
footer.pack(fill='x', side='bottom')

lbl_country = ttk.Label(
    master=header,
    text='Choose (or type in) a country:',
)
lbl_country.grid(row=0, column=0, sticky='nw', padx=(5, 0))

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
mnu_countries = SearchableCombobox(
    master=header,
    values=countries,
)
mnu_countries.grid(row=0, column=1, sticky='new', padx=5)

tips = ToolTip(master=mnu_countries,
               text='Type a country\'s name in, or type some letters and hit enter to show the countries with the typed letters in the corresponding order\n'
                    'E.g. "ez" will show Belize "B(e)li(z)e", New Zealand "N(e)w (Z)ealand", Venezuela "V(e)ne(z)uela",... (non-case sensitive)')

dir_flags_log = f'{os.getenv("LocalAppData")}\\Flags'
os.makedirs(dir_flags_log, exist_ok=True)
dir_flags = f'{os.getenv("AppData")}\\Flags'
os.makedirs(dir_flags, exist_ok=True)
def get_hash(file: str or bytes) -> str:
    """
    Returns SHA3-256 hex of a file, using either the file's path (for log file) or binary data (for image files)
    """

    if type(file) is str:
        with open(file, 'rb') as f:
            return sha3_256(f.read()).hexdigest()
    else:
        return sha3_256(file).hexdigest()


def cache_flag(country: str, img: bytes) -> None:
    """
    Store image of selected countries' flags, when they were cached, and hash of stored images in %AppData%\Roaming\Flags
    """

    # if log file not exists | log_hash not exists | hash of log file is not equal to log_hash data: make new log file
    if not os.path.exists(f'{dir_flags_log}\\log') or not os.path.exists(f'{dir_flags_log}\\log_hash') \
            or get_hash(f'{dir_flags_log}\\log') != open(f'{dir_flags_log}\\log_hash').read():
        with open(f'{dir_flags_log}\\log', 'w') as log:
            log.write('{}')

    with open(f'{dir_flags_log}\\log') as log:
        cache_log = literal_eval(log.read())

    with open(f'{dir_flags}\\{country}.png', 'wb') as image:
        image.write(img)

    cache_log[country] = (int(time()), get_hash(img))
    with open(f'{dir_flags_log}\\log', 'w') as log:
        log.write(str(cache_log))

    with open(f'{dir_flags_log}\\log_hash', 'w') as log_hash:
        log_hash.write(get_hash(f'{dir_flags_log}\\log'))


def get_cache(country: str) -> bool | bytes:
    """
    Returns path to image in cache if available and image is less than 1 week old,
    or returns False otherwise
    """

    # if .png of flag not exists | log file not exists | log_hash not exists | hash of log file is equal to log_hash data: False
    if not os.path.exists(f'{dir_flags}\\{country}.png') or not os.path.exists(f'{dir_flags_log}\\log') \
            or not os.path.exists(f'{dir_flags_log}\\log_hash') \
            or get_hash(f'{dir_flags_log}\\log') != open(f'{dir_flags_log}\\log_hash').read():
        return False

    with open(f'{dir_flags_log}\\log') as file:
        log = literal_eval(file.read())

    # if country not in cache log | flag image older than 1 week | hash of image is not equal to recorded hash: False
    cached = log.get(country, False)
    if not cached or int(time()) - cached[0] > 604800 or get_hash(f'{dir_flags}\\{country}.png') != cached[1]:
        return False

    with open(f'{dir_flags}\\{country}.png', 'rb') as file:
        return file.read()


def get_image(country: str) -> (ttk.Label, str):
    """
    Get image of flag of selected country from cache,
    if none found, fetch flag from Wikimedia and cache it.
    Returns image of flag, and name of .svg image file (to be used in credits) if successful,
    or returns error message, and empty string as name of .svg file otherwise
    """

    img = get_cache(country)
    if img:
        wiki_file = f'Flag_of_{"_".join(country.split(" "))}.svg'
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
            lbl_error_msg = ttk.Label(
                master=body,
                text='JSON fetch request timed out. Please retry by reselecting the country.',
                style='Error.TLabel'
            )
            return lbl_error_msg, ''

        except requests.exceptions.HTTPError:
            lbl_error_msg = ttk.Label(
                master=body,
                text=f'HTTP Error while fetching JSON. Code: {re.status_code}.\nMessage: {re.reason}',
                style='Error.TLabel'
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
            json = json['query']['pages'].popitem()[1]  # value of str(pageid_number): {...}

            re = requests.get(json['thumbnail']['source'],
                              timeout=1,
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'})
            re.raise_for_status()
            img = re.content
            cache_flag(country, img)
            wiki_file = json['pageimage']

        except requests.exceptions.Timeout:
            lbl_error_msg = ttk.Label(
                master=body,
                text='Image fetch request timed out. Please retry by reselecting the country.',
                style='Error.TLabel'
            )
            return lbl_error_msg, ''

        except requests.exceptions.HTTPError:
            lbl_error_msg = ttk.Label(
                master=body,
                text=f'HTTP Error while fetching image. Code: {re.status_code}.\nMessage: {re.reason}',
                style='Error.TLabel'
            )
            return lbl_error_msg, ''

    img = ImageTk.PhotoImage(file=BytesIO(img))
    img_flag = ttk.Label(
        master=body,
        image=img,
        anchor='center'
        )
    img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
    return img_flag, wiki_file


def get_credit(wiki_file: str) -> (ttk.Label, ttk.Label | tk.Entry):
    """
    Returns credit, and a selectable link to .svg flag image file on Wikimedia
    if wiki_file isn't empty (meaning get_image was successful),
    or returns two empty labels otherwise
    """

    if wiki_file == '':
        return ttk.Label(footer), ttk.Label(footer)

    lbl_credit = ttk.Label(
        master=footer,
        text='Images courtesy of Wikimedia Commons. Source: ',
    )
    lbl_credit_link = tk.Entry(
        master=footer,
        width=len(f'https://commons.wikimedia.org/wiki/File:{wiki_file}'),
        readonlybackground='light gray',
        borderwidth=0,
        font=('Segoe UI', 9),
    )
    lbl_credit_link.insert(0, f'https://commons.wikimedia.org/wiki/File:{wiki_file}')
    lbl_credit_link.configure(state='readonly')
    lbl_credit_link.bind('<FocusIn>', lambda _:lbl_credit_link.selection_range(0, 'end'))
    return lbl_credit, lbl_credit_link


def show_flag() -> None:
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


root.mainloop()
