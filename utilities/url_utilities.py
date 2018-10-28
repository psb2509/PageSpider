import re
import string
from urllib.request import urlopen

# Fix Starts : urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
# https://www.python.org/dev/peps/pep-0476/
# https://github.com/googleapis/google-api-python-client/issues/478
# https://stackoverflow.com/questions/19699367/unicodedecodeerror-utf-8-codec-cant-decode-byte
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
# Fix Ends : urllib.error.URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed

from bs4 import BeautifulSoup


def load_urls_from_file(file_path: str):
    try:
        with open(file_path) as f:
            content = f.readlines()
            return content
    except FileNotFoundError:
        print("the file " + file_path + " could not be found")
        exit(2)


def load_page(url: str):
    response = urlopen(url)
    html = response.read().decode("ISO-8859-1")
    return html


def scrape_page(page_contents: str):
    chicken_noodle = BeautifulSoup(page_contents, "html5lib")

    for script in chicken_noodle(["script", "style"]):
        script.extract()

    text = chicken_noodle.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    text = ' '.join(chunk for chunk in chunks if chunk)
    plain_text = ''.join(filter(lambda x: x in string.printable, text))

    clean_words = []

    words = plain_text.split(" ")
    for word in words:
        clean = True

        # no punctuation
        for punctuation_marks in string.punctuation:
            if punctuation_marks in word:
                clean = False

                # no numbers
            if any(char.isdigit() for char in word):
                clean = False

                # at least two characters but no more than 10
            if len(word) < 2 or len(word) > 10:
                clean = False

            if not re.match(r'^\w+$', word):
                clean = False

            if clean:
                try:
                    clean_words.append(word.lower())
                except UnicodeEncodeError:
                    print(".")

    return clean_words
