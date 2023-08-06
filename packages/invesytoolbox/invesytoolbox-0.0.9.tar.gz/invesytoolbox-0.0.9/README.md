# invesytoolbox

A set of useful tools, created for my own convenience, but you might find it useful too.

Why "invesy"? Invesy (from German **In**halts**ve**rwaltungs**sy**stem == content management system) is a closed source cms I created with Thomas Macher. It's only used in-house, that's why we didn't bother making it open source.

Invesy runs on Zope, so most of the individual website's logic runs in restricted Python. That's one reason for this toolbox: providing a set of useful functions in one single package which can be allowed in our restricted Python environment without having to allow a long list of external packages.

That's also why all date and time functions also take into account the old DateTime (as opposed to datetime) package, on which Zope is still relying upon heavily.

# What's in the box?
- data_tools
- date\_time\_tools
- email\_phone\_tools
- locales_tools
- restricted\_python\_tools
- security_tools
- terminal_tools
- text_name_tools

## data_tools
- **dict\_from\_dict\_list**: Create a dictionary from a list of dictionaries. You need to provide the key that's to be used.
- **create_vcard**: Provide a dictionary, get a vCard.
- **dict_2unicode**
  - Converts all keys and values in a dictionary from bytes to unicode.
  - All keys and values are changed from bytes to unicode, if applicable.
  - Other data types are left unchaged, including other compound data types.
- **value_2datatype**: Convert a value to a datatype. This function has two modes:
	1. it uses a json file with the metadata (types of variables by name)
	2. it makes educated guesses in converting a string (don't feed bytes to this function!)
- **dict_2datatypes**: Converts all data of a dictionary to specific (json metadata) or guessed types using *value_2datatype*.
- **sort_dictlist**: Sorts a list of dictionaries. A single or multiple keys can provided for sorting.

## date\_time\_tools
- **get_dateformat**: Guess the correct format string (like `%d.%m.%Y`) to correctly convert a string to some date format (datetime.datetime, datetime.date or DateTime.DateTime).
- **str\_to\_dt**: convert a string to datetime.datetime
- **str\_to\_DT**: convert a string to DateTime.DateTime
- **str\_to\_date**: convert a string to datetime.date
- **DT\_to\_dt**: convert DateTime.DateTime to datetime.datetime
- **DT\_to\_date**: convert DateTime.DateTime to datetime.date
- **date\_to\_dt**: convert datetime.date to datetime.datetime
- **date\_to\_DT**: convert datetime.date to DateTime.DateTime
- **convert_datetime**: Using the convert-functions above, convert a date, time or string to any other type.
- **get\_calendar\_week**: Get the calendar week from a date, time or string.
- **get\_dow\_number**: Get the day of week number from a string or a date and time format.
- **get_isocalendar**: Get the isocalendar tuple (year, week, dow nb) of a date, time or string.
- **get_monday (obsolete)**: from year and week.
- **daterange\_from\_week**: Get the first and last day of a week.
- **dates\_from\_week**: Get all days of a week.
- **day\_from\_week**: Get a specific day from a week.
- **monday\_from\_week**: self explanatory
- **last\_week_of\_year**: Get the last week of the year (sometimes 52, sometimes 53)

## email\_phone\_tools
- **create\_email\_message**: Create an email message (no sending)
- **process_phonenumber**
	- Processes a phonenumber and returns it in international format.
	- Checks if a phonenumber is valid

## locales_tools
- **get_locale**: Get the current locale, returns a dictionary containing (with examples):
	- locale (tuple): ('de_AT', 'utf-8')
	- locale_string: 'de_AT'
	- language: 'de'
	- country: 'AT'
	- currency: 'EUR'
- **fetch\_all\_countries**: Returns a tuple, a list, a dictionary or a dictionary of dictionaries.
- **format_price**: Formats a price according to the locale, ex: 4537 -> `€ 4.537,-`
- **get_country**: Returns all the data for a country as a dictionary.
- **get\_language\_name**: Returns the name of a given language code in a language of choice.
- **fetch_holidays**: Fetch the official holidays for a country in a specific period of time (given in years or a date range).
- **is_holiday**: Check if a date is a holiday in a specific country (or in your current locale).

## security_tools
- **create_secure_key**: Generate a key (default 256 bit)
- **create_key**: Create a key or password
- **check\_password\_security**: Checks if a password (or any string) meets certain criteria

## terminal_tools
- **print_**: Enhanced print function, specially enhanced for printing in the terminal.
- **wait\_for\_key**: Wait for a pressed key to continue.

## text\_name\_tools
- **and_list**: creates a human-readable list, including "and" (or any similar word, i.e. in another language), like

	```
	1, two, Three and 4
	```

- **capitalize_text**: Capitalize text or names. This is specially handy for names which otherwise would be capitalized wrongly with string's "title" method like:
	- Conan McArthur
	- Susanne Mayr-Grünwald
	- Maria de Angelis
- **get_gender** of a prename.
- **leet**: Create a leet from any string. 
	`Georg --> 630r9`
- **sort_names**: Sorts by name, prename: splits only at the last space before sorting.
	Correctly sorts names
	- with special characters, like umlauts
	- combined names
	- names with prefixes (like de or von)

	examples:

	- Maria de Angelis
	- Susanne Mayr-Grünwald

- **map\_special\_chars**
Converts any string to ascii, sometimes converting a single character to two, like for German umlauts (only if sort == False):
	
	```
	ä --> ae
	ö --> oe
	ü --> ue
	ß --> ss
	```

- **sort_word_list**: Sort a list of words using map\_special\_chars.
