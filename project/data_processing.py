from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import json

#filepath = "sec-edgar-filings\\GE\\10-K\\0001193125-11-047479\\full-submission.txt"


def read_file(filepath):
    """
    Reads the entire content of a file located at the specified filepath.

    Args:
    filepath (str): Path to the file to be read.

    Returns:
    str: Content of the file as a string, or None if the file doesn't exist or an error occurs.
    """
    if not os.path.exists(filepath):
        print("File does not exist:", filepath)
        return None
    try:
        with open(filepath, 'rb') as file:
            content = file.read()
            content = content.replace(b'\x00', b'')
        return content.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def process(filepath):
    """
    Processes a specified 10-K filing document to extract sections based on regex patterns and store their content
    into a DataFrame. It looks for the documents within the file, finds specific items (like Item 1A, 7, etc.), and
    extracts their content after processing HTML tags and spaces.

    Args:
    filepath (str): Path to the SEC filing document.

    Returns:
    str: Extracted content from the specified sections of the 10-K document, or None if not found or on error.
    """
    raw_10k = read_file(filepath)
    if raw_10k is None:
        print(f"No data to process in {filepath}")
        return None

    # initialize regular expressions
    doc_start_pattern = re.compile(r'<DOCUMENT>')
    doc_end_pattern = re.compile(r'</DOCUMENT>')
    type_pattern = re.compile(r'<TYPE>[^\n]+')

    # find document sections
    starts = [match.end() for match in doc_start_pattern.finditer(raw_10k)]
    ends = [match.start() for match in doc_end_pattern.finditer(raw_10k)]
    types = [match.group()[len('<TYPE>'):] for match in type_pattern.finditer(raw_10k)]

    document = {}
    for dtype, start, end in zip(types, starts, ends):
        if '10-K' in dtype:
            document[dtype] = raw_10k[start:end]

    if '10-K' not in document:
        print("No 10-K document found in file.")
        return None

    # extract items using regex
    regex = re.compile(r'(>Item\s*(?:<[^>]+>)*\s*(1A|1B|7A|7|8)\.{0,1})|(ITEM\s*(?:<[^>]+>)*\s*(1A|1B|7A|7|8))', re.IGNORECASE)
    matches = regex.finditer(document['10-K'])
    #if not matches:
    #    print("No matches found for specified items.")
    #    return None

    # create DataFrame from matches
    for match in matches:
        print(match)
    matches = regex.finditer(document['10-K'])


    match_list = [(match.group(), match.start(), match.end()) for match in matches]
    if match_list:
        test_df = pd.DataFrame(match_list, columns=['item', 'start', 'end'])
    else:
        print("No data to populate DataFrame.")
        return None

    test_df.columns = ['item', 'start', 'end']
    test_df['item'] = test_df.item.str.lower()
    test_df.replace({'&#160;': ' ', '&nbsp;': ' ', ' ': '', '\\.': '', '>': ''}, regex=True, inplace=True)

    # drop duplicates and set DataFrame index
    pos_dat = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    pos_dat.set_index('item', inplace=True)

    if not 'item7a' in pos_dat.index:
        print(f"'Item 7a' not found in {filepath}")
        return None

    if 'item7' in pos_dat.index:
            item_1a_raw = document['10-K'][pos_dat.loc['item7', 'start']:pos_dat.loc['item7a', 'end']]
            item_1a_content = BeautifulSoup(item_1a_raw, 'lxml').get_text("\n\n", strip=True)

            words_to_skip = 430  # number of words to skip
            item_1a_content = ' '.join(item_1a_content.split()[words_to_skip:])
            return item_1a_content

    else:
            print(f"'Item 7' not found in {filepath}")
            return None


def get_text_content(html_content, limit=1000):
    """
    Converts HTML content to plain text.

    Args:
    html_content (str): HTML content to convert.
    limit (int): Maximum number of characters to return.

    Returns:
    str: Plain text content extracted from HTML, truncated to 'limit' characters if specified.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text("\n\n", strip=True)
    return text[:limit] if limit else text


results = {}
def process_directory(root_directory, results):
    """
    Walks through all files in a specified directory, processing each 'full-submission.txt' file found. Extracts and
    processes text from these files, then stores the results in a dictionary.

    Args:
    root_directory (str): Directory to search for files.
    results (dict): Dictionary to store the results.

    Returns:
    dict: Updated dictionary with paths as keys and processed text content as values.
    """
    for root, dirs, files in os.walk(root_directory):
        for filename in files:
            if filename == 'full-submission.txt':
                filepath = os.path.join(root, filename)
                print(f"Processing file: {filepath}")
                processed = process(filepath)
                if processed is not None:
                    next_p = get_text_content(processed)
                    results[f'{filepath}'] = next_p
                else:
                    print(f"No valid data to process for file: {filepath}")
    return results


def run(ticker):
    """
    Processes all 10-K filings for a given ticker symbol. This function constructs a directory path based on the ticker,
    processes the directory, and saves the results to a JSON file.

    Args:
    ticker (str): The ticker symbol for which 10-K filings are processed.

    Outputs:
    Saves a JSON file containing processed data from the 10-K filings.
    """
    first = "sec-edgar-filings/"
    last = "/10-K"
    root_directory = first + ticker + last
    print(root_directory)
    results = {}

    resultss = process_directory(root_directory, results)
    json_filepath = 'sec_data.json'
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(resultss, f, ensure_ascii=False, indent=4)
    print(f"Data truncated and saved to {json_filepath}")

