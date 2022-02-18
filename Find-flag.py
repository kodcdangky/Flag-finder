"""
Flag-finder 1.2.0
A small program to fetch and display flag of selected country from Wikimedia's database
---------------------------------------------------------------------------------------

Design choice:
- Small, minimalistic
- Light gray background to help flags with color white at the border stands out

Dependencies:
- requests v2.27.1
- Pillow v9.0.0
"""
import os
import tkinter as tk
import tkinter.ttk as ttk
from io import BytesIO
from hashlib import sha3_256
from time import time
from ast import literal_eval
from fnmatch import fnmatch
from string import ascii_lowercase
from subprocess import run

# External packages
import requests
from PIL import ImageTk


FLAGS_LOG_DIR = os.path.join(os.getenv("LocalAppData"), "Flags")
FLAGS_DIR = os.path.join(os.getenv("AppData"), "Flags")
if os.name.startswith('nt'):
    EXPLORER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")


class SearchableCombobox(ttk.Combobox):
    """
    A ttk.Combobox whose entry field comes with autocompletion and can be used as a search bar (non-case sensitive)
    Calls the assigned function when an element was typed correctly/selected

    :param no_match_msg: Message to show on top of menu when no matching elements are found
    :param function: Callback function when an element is chosen
    :param func_args: Arguments for callback function
    :param kwargs: All keyword arguments accepted by ttk.Combobox.__init__()
    """
    def __init__(self,
                 no_match_msg: str = '<No match found, try a different pattern or select from the list below>',
                 function = None,
                 *func_args,
                 **kwargs):
        super().__init__(**kwargs)
        self.__no_match_msg = str(no_match_msg)
        self.__function = function if callable(function) and not isinstance(function, type) else None
        self.__func_args = func_args
        self.__values = self['values']  # The real value list of the CBox, while the seen list is dynamically changed depending on what's typed in
        self.bind('<KeyRelease>', self.__autocomplete)
        self.bind('<<ComboboxSelected>>', self.__selected)
        self.bind('<Return>', self.__selected)
        self.bind('<FocusIn>', lambda _: self.selection_range(0, 'end'))

    def __selected(self, _) -> None:
        """
        Internally called only

        Changes Combobox's dropdown depending on what is typed in by user.
        Shows the dropdown list with elements with the letters typed in, in the corresponding order,
        or if an element was typed correctly/selected, call the assigned function
        """
        # Only accepts letters and spaces
        if not ''.join(self.get().split(' ')).isalpha():
            return

        if self.get() not in self.__values:
            matching_elem = []

            for elem in self.__values:
                if len(self.get()) > len(elem):
                    continue

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
                matching_elem.append(self.__no_match_msg)
                matching_elem.append('--------------------')
                matching_elem.extend(self.__values)
                self.configure(width=len(self.__no_match_msg))

            self.configure(postcommand=super(SearchableCombobox, self).configure(values=matching_elem))
            self.event_generate('<Down>')
            self.configure(postcommand=super(SearchableCombobox, self).configure(values=self.__values))
        elif self.__function:
            self.__function(*self.__func_args)

    def __autocomplete(self, event) -> None:
        """
        Internally called only

        Automatically completes the combobox entry field with the first element's name found that matches exactly with what
        has been typed in so far, continuously update the autocompletion as user continues typing
        """
        typed = self.get()
        # <event.state> = 8 -> No modifiers (irrelevant)
        #               = 9 -> Shift (irrelevant)
        #               = 12 -> Ctrl
        #               = 13 -> Ctrl+Shift
        #               = 131080 -> Alt
        #               = 131081 -> Alt+Shift
        #               = 131084 -> Ctrl+Alt
        #               = 131085 -> Ctrl+Alt+Shift
        #               = ... -> To be discovered
        if not ''.join(typed.split(' ')).isalpha() or typed in self.__values \
                or event.state in (12, 13, 131080, 131081, 131084, 131085) \
                or event.keysym.lower() not in tuple(ascii_lowercase):
            return

        for elem in self.__values:
            if len(typed) > len(elem):
                continue

            if fnmatch(elem, f'{typed}*'):
                self.set(elem)
                self.selection_range(len(typed), 'end')
                self.icursor('end')
                break

    def configure(self, **kwargs) -> None:
        """
        Configure resources of this Combobox

        :param kwargs: All keyword arguments accepted by ttk.Combobox.configure(), plus 'function', 'args', 'no_match_msg'
        :key no_match_msg:  Message to show on top of menu when no matching elements are found
        :key function: Callback function when an element is chosen
        :key func_args: Arguments for callback function, passed in a tuple or list
        """
        if 'no_match_msg' in kwargs:
            self.__no_match_msg = str(kwargs.pop('no_match_msg'))

        if 'function' in kwargs:
            if callable(kwargs['function']) and not isinstance(kwargs['function'], type):
                self.__function = kwargs.pop('function')
            else:
                raise TypeError('Keyword "function" only accepts callable functions')

        if 'func_args' in kwargs:
            if isinstance(kwargs['func_args'], (list, tuple)):
                self.__func_args = kwargs.pop('func_args')
            else:
                raise TypeError('Keyword "func_args" only accepts tuple or list')

        if 'values' in kwargs:
            if isinstance(kwargs['values'], (list[str], tuple[str, ...])):
                self.__values = kwargs['values']
        super().configure(**kwargs)
    config = configure


class ToolTip:
    """
    An appear-on-hover-at-mouse-location tooltip. Works with a tkinter widget master
    Credit: https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter/36221216#36221216

    :param master: tk/ttk widget that binds ToolTip (default: None)
    :type master: tk.Widget | ttk.Widget
    :param text: Message to show on tooltip (default: '')
    :type text: str
    :param delay: delay duration before showing the tooltip (in milliseconds) (default: 500)
    :type delay: int
    """
    def __init__(self, master: tk.Widget | ttk.Widget = None, text: str = '', delay: int = 500):
        self.master = master
        self.text = text
        self._tip_window = None
        self._id = None
        self.delay = delay
        self.master.bind('<Enter>', self._enter)
        self.master.bind('<Leave>', self._leave)
        self.master.bind('<Button>', self._leave)

    def _enter(self, _):
        self._schedule()

    def _leave(self, _):
        self._unschedule()
        self._hidetip()

    def _schedule(self):
        self._unschedule()
        self._id = self.master.after(self.delay, self._showtip)

    def _unschedule(self):
        if self._id:
            self.master.after_cancel(self._id)
        self._id = None

    def _showtip(self):
        if self._tip_window or not self.text:
            return

        self._tip_window = tk.Toplevel(self.master)

        self._tip_window.overrideredirect(True)
        self._tip_window.geometry(f'+{self.master.winfo_pointerx() + 10}+{self.master.winfo_pointery() + 10}')

        label = tk.Label(master=self._tip_window,
                         text=self.text,
                         justify='left',
                         background='#ffffe0',
                         relief='solid',
                         borderwidth=1,
                         font=('Segoe UI', '9'))
        label.pack()
        self._tip_window.bind('<Enter>', self._leave)

    def _hidetip(self):
        if self._tip_window:
            self._tip_window.destroy()
        self._tip_window = None


# Greeting window: a small window with a label and a dropdown list of countries for user to choose from
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
mnu_countries = SearchableCombobox(master=header, values=countries)
mnu_countries.grid(row=0, column=1, sticky='new', padx=5)
ToolTip(master=mnu_countries,
        text='Type a country\'s name in, or type some letters and press enter to show the countries with the typed letters in the corresponding order\n'
             'E.g. "ez" will show Belize "B(e)li(z)e", New Zealand "N(e)w (Z)ealand", Venezuela "V(e)ne(z)uela",... (non-case sensitive)')

os.makedirs(FLAGS_LOG_DIR, exist_ok=True)
os.makedirs(FLAGS_DIR, exist_ok=True)


def get_hash(file: str) -> str:
    """
    Returns SHA3-256 hex of a file, given its path

    :param file: to-be-hashed file's path
    :return: hex hash of file
    """
    with open(file, 'rb') as f:
        return sha3_256(f.read()).hexdigest()


def cache_flag(country: str, img: bytes) -> None:
    """
    Store image of selected countries' flags, when they were cached, and hash of stored images in %AppData%\\Roaming\\Flags

    :param country: name of country's flag to be cached
    :param img: content of img file in bytes
    """
    # if log file not exists | log_hash not exists | hash of log file is not equal to log_hash data: make new log file
    if not (os.path.exists(os.path.join(FLAGS_LOG_DIR, 'log'))
            and os.path.exists(os.path.join(FLAGS_LOG_DIR, 'log_hash'))
            and get_hash(os.path.join(FLAGS_LOG_DIR, 'log')) == open(os.path.join(FLAGS_LOG_DIR, 'log_hash')).read()):
        with open(os.path.join(FLAGS_LOG_DIR, 'log'), 'w') as log:
            log.write('{}')

    with open(os.path.join(FLAGS_LOG_DIR, 'log')) as log:
        cache_log = literal_eval(log.read())

    with open(os.path.join(FLAGS_DIR, f'{country}.png'), 'wb') as image:
        image.write(img)

    cache_log[country] = (int(time()), get_hash(os.path.join(FLAGS_DIR, f'{country}.png')))
    with open(os.path.join(FLAGS_LOG_DIR, 'log'), 'w') as log:
        log.write(str(cache_log))

    with open(os.path.join(FLAGS_LOG_DIR, 'log_hash'), 'w') as log_hash:
        log_hash.write(get_hash(os.path.join(FLAGS_LOG_DIR, 'log')))


def get_cache(country: str) -> str | None:
    """
    Returns path to image in cache if available and image is less than 1 week old,
    or returns None otherwise

    :param country: name of country to return the cached flag of
    :return: path to image in cache | None
    """
    # if .png of flag not exists | log file not exists | log_hash not exists | hash of log file is equal to log_hash data: None
    if not (os.path.exists(os.path.join(FLAGS_DIR, f'{country}.png'))
            and os.path.exists(os.path.join(FLAGS_LOG_DIR, 'log'))
            and os.path.exists(os.path.join(FLAGS_LOG_DIR, 'log_hash'))
            and get_hash(os.path.join(FLAGS_LOG_DIR, 'log')) == open(os.path.join(FLAGS_LOG_DIR, 'log_hash')).read()):
        return None

    with open(os.path.join(FLAGS_LOG_DIR, 'log')) as file:
        log = literal_eval(file.read())

    # if country not in cache log | flag image older than 1 week | hash of image is not equal to recorded hash: None
    cached = log.get(country, None)
    if not (cached
            and int(time()) - cached[0] <= 604800
            and get_hash(os.path.join(FLAGS_DIR, f'{country}.png')) == cached[1]):
        return None

    return os.path.normpath(os.path.join(FLAGS_DIR, f'{country}.png'))


def get_image(country: str) -> (ttk.Label, str):
    """
    Get image of flag of selected country from cache,
    if none found, fetch flag from Wikimedia and cache it.

    :param country: name of country to get flag of
    :return: flag's image, and name of .svg file | error message, and empty string
    """
    img_path = get_cache(country)
    if img_path:
        wiki_file = f'Flag_of_{"_".join(country.split(" "))}.svg'
        with open(img_path, 'rb') as file:
            img = file.read()
    else:
        try:
            img_width = 700  # flag's width, aspect ratio preserved
            param_api = {'action': 'query',
                         'format': 'json',
                         'prop': 'pageimages',
                         'titles': f'File:Flag of {country}.svg',
                         'pithumbsize': img_width}
            re = requests.get("https://commons.wikimedia.org/w/api.php",
                              timeout=1,
                              headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0'},
                              params=param_api)
            re.raise_for_status()

        except requests.exceptions.Timeout:
            lbl_error_msg = ttk.Label(
                master=body,
                text='JSON fetch request timed out. Please retry by re-selecting the country.',
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
                text='Image fetch request timed out. Please retry by re-selecting the country.',
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
        anchor='center',
        )
    img_flag.image = img  # what the fuck is this sorcery https://stackoverflow.com/a/34235165
    if os.name.startswith('nt'):
        img_flag.configure(cursor='hand2')
        img_flag.bind('<ButtonRelease-1>',
                      lambda _: run([EXPLORER_PATH, '/select,', img_path if img_path else get_cache(country)]))
        ToolTip(master=img_flag,
                text='Click the flag to see all cached flags\n'
                     'To cache a flag, select its country from the dropdown menu')

    return img_flag, wiki_file


def get_credit(wiki_file: str) -> (ttk.Label, ttk.Label | tk.Entry):
    """
    Returns credit, and a selectable link to .svg flag image file on Wikimedia
    if wiki_file isn't empty (meaning get_image was successful),
    or returns two empty labels otherwise

    :param wiki_file: name of .svg file
    :return: credit and link | 2 empty ttk.Label
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
    lbl_credit_link.bind('<FocusIn>', lambda _: lbl_credit_link.selection_range(0, 'end'))
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


mnu_countries.configure(function=show_flag)
mnu_countries.focus_set()

root.mainloop()
