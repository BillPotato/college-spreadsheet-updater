#!python 3

# Stats that can be updated:
# "school population", "location", "overall ranking", "setting", "acceptance", "sat", "act", "gpa"

import ezsheets, requests
from bs4 import BeautifulSoup
from threading import Thread
from tqdm import tqdm
from json.decoder import JSONDecodeError # Error handling
import confiq # File
from state_abbreviations import state_abbreviations_dict # File

# prevent blocking
newheaders = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64)'
    # Alternative: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
}

# Custom threading class to return value
class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

# Fetch spreadsheet
def get_spreadsheet_rows(sheet_id):
    print("Fetching spreadsheet...")
    spreadsheet = ezsheets.Spreadsheet(sheet_id)[0]
    rows = spreadsheet.getRows()
    print("Fetched spreadsheet...")
    return rows

def update_spreadsheet(sheet_id, rows):
    print("Uploading spreadsheet...")
    spreadsheet = ezsheets.Spreadsheet(sheet_id)[0]
    spreadsheet.updateRows(rows)
    print("Spreadsheet uploaded!")
    
# Find where all the columns of info that can be updated are
# FIELDS = "school population", "location", "overall ranking", "setting", "acceptance", "sat", "act", "gpa"]
def generate_key_columns(sheet: list, FIELDS) -> dict:
    key_columns = {}
    for column, header in enumerate(sheet[0]):
        if header.lower() in FIELDS:
            key_columns[column] = header.lower()
    return key_columns

def get_updatable_college_rows(sheet: list, key_columns: dict[int, str]) -> list[int]:
    colleges = sheet[1:] #remove header row
    updatable_rows = []
    row = 0 # start at row 1 (row 0 is header)
    while colleges[row][0]:
        for column in key_columns:
            if not colleges[row][column]: # if missing column -> college is updatable
                updatable_rows.append(row+1) # +1 because removed first row
                break
            else: pass
        row +=1
    return updatable_rows


def update_college(college, key_columns):
    
    college_name = college[0]
    
    # Find missing KEY columns
    updatable_columns = []
    for column in key_columns:
        if not college[column]:
            updatable_columns.append(column)
        else: pass
    
    # Fetch the results page for the "{college_name}" search
    results_page = requests.get("https://www.usnews.com/search?q=" + college_name, headers =  newheaders)
    results_page.raise_for_status()
    results_soup = BeautifulSoup(results_page.text, "html.parser")
    
    # Fetch first result's link
    first_result_tag = results_soup.select("a.Anchor-byh49a-0.MediaObjectBox__AnchorWrap-sc-7ytr6b-5.eMEqFO.bbyhFG")[0]
    college_page = requests.get(first_result_tag.get("href"), headers = newheaders)
    college_page.raise_for_status()
    college_soup = BeautifulSoup(college_page.text, "html.parser")
    
    # Fill in the missing columns
    for updatable_column in updatable_columns:
        missing_info = key_columns[updatable_column]
        try:
            college[updatable_column] = get_info(missing_info, college_soup)
        except IndexError:
            college[updatable_column] = "Error: Could not find! (check school name)"     
    return college


def get_info(missing_info: str, college_soup) -> str: # college_soup is of type BeautifulSoup
    
    tag_text = "Error: Could not match missing_info! (Please report to dev)"
    # Error handler (just in case)
    
    match missing_info:
        case "overall ranking":
            selector = "span.Villain__RankingSpan-sc-8s66oj-4.fDSmVR > span"
            tag_text = college_soup.select(selector)[0].getText()[1:]
        case "location":
            selector = "span.NuggetsContainer__LocationSpan-sc-108otk5-0.GXzCk.mr2"
            tag_text = college_soup.select(selector)[0].getText()
            tag_text = tag_text[tag_text.find("•")+2:]
            state_portion = tag_text[-2:]
            tag_text = tag_text.replace(state_portion, state_abbreviations_dict[state_portion])
        case "setting":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[0].getText()
        case "school population":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[2].getText()
        case "acceptance":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[3].getText()
        case "sat":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[4].getText()
        case "act":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[5].getText()
        case "gpa":
            selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
            tag_text = college_soup.select(selector)[6].getText()
    return tag_text
        
    
def main():
    try:
        spreadsheet_rows = get_spreadsheet_rows(confiq.spreadsheet_id)
    except JSONDecodeError as e:
        print(f"Error: {e} while fetching. Try again!")
        
    key_columns = generate_key_columns(spreadsheet_rows, confiq.FIELDS)
    updatable_rows = get_updatable_college_rows(spreadsheet_rows, key_columns)
    
    # start fetching information
    college_threads = []
    for row in updatable_rows:
        college_thread = ThreadWithReturnValue(target=update_college, args=[spreadsheet_rows[row], key_columns])
        college_threads.append(college_thread)
        college_thread.start()
    
    bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} {unit}"
    for thread_idx, row in enumerate(tqdm(updatable_rows, desc="Updating colleges", unit="colleges", bar_format=bar_format)):
        spreadsheet_rows[row] = college_threads[thread_idx].join()
        thread_idx +=1

    try:
        update_spreadsheet(confiq.spreadsheet_id, spreadsheet_rows)
    except JSONDecodeError as e:
        print(f"Error: {e} while uploading. Try again!")
    
    
if __name__ == "__main__":
    main()
