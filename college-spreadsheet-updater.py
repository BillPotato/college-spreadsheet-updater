#!python 3

# Stats that can be updated:
# "school population", "location", "overall ranking", "setting", "acceptance", "sat", "act", "gpa"

import requests
import ezsheets
import time
import re
import random
from typing import Type
from bs4 import BeautifulSoup
from threading import Thread
from tqdm import tqdm
from json.decoder import JSONDecodeError # For error handler
import confiq # File
import state_abbreviations # File


# Prevent blocking
newheaders = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64)'
#     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
}


class college_sheet:
    
    def __init__(self, sheet_id):
        self.sheet_id: str = sheet_id
        self.spreadsheet_obj: Type[ezsheets.Sheet] = ezsheets.Spreadsheet(sheet_id)[0]
        self.rows: list[list] = self.spreadsheet_obj.getRows()
        self.college_name_column = self.spreadsheet_obj.getColumn(1) # don't remove header
        self.key_columns: dict[int, str] = {}
        self.unfilled_colleges: list[college] = []
        self.college_threads: list[Type[Thread]] = []
        
        
    def upload_spreadsheet(self):
        
        print("Uploading spreadsheet...")
        self.spreadsheet_obj.updateRows(self.rows)
        print("Spreadsheet uploaded!")
    
    def generate_key_columns(self, FIELDS: list[str]):
        headers = self.rows[0]
        for column, header in enumerate(headers):
            if header.lower() in FIELDS:
                self.key_columns[column] = header.lower()
            else: pass

    def get_unfilled_college_rows(self):

        for row, college_name in enumerate(self.college_name_column[1:]):
            if not(re.compile(r"^(\s)*$").search(college_name)):
            # ^checks if there are characters other than space/tab/newline in string
                college_obj = college(row +1, self.rows[row +1])
                
                if not college_obj.is_filled(self.key_columns):
                    self.unfilled_colleges.append(college_obj)
                else: pass # college is filled
            else: pass # no college to check

        
    def fill_unfilled_colleges(self):
        college_updating_threads = []
        bar_format = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} {unit}"
        
        for college in tqdm(self.unfilled_colleges, desc="Creating threads", unit="threads", bar_format=bar_format):
            time.sleep(random.uniform(0.1, 0.3))
            college_updating_thread = Thread(target=college.update, args=[self.key_columns])
            college_updating_threads.append(college_updating_thread)
            college_updating_thread.start()
        
        for college_updating_thread in tqdm(college_updating_threads, desc="Updating colleges", unit="colleges", bar_format=bar_format):
            college_updating_thread.join()
            
        for college in tqdm(self.unfilled_colleges, desc="Applying changes", unit="colleges", bar_format=bar_format):
            self.rows[college.row_idx] = college.row
        
class college:
    
    def __init__(self, row_idx: int, row: list):
        self.row_idx: int = row_idx # index in college_sheet.rows
        self.row: list = row
        self.name: str = self.row[0]
        self.unfilled_cells: list[int] = []
        
    
    def is_filled(self, key_columns: dict[int, str]): # This func also modifies self.unfilled_cells
        filled_status = True
        for column in key_columns:
            if not self.row[column]:
                self.unfilled_cells.append(column)
                filled_status = False
            else: pass
        return filled_status
        
    def update(self, key_columns): # Run is_filled first
        
        def get_stat(missing_stat: str, college_soup): # college_soup is of type BeautifulSoup
            
            tag_text = "Error: Could not match missing_stat! (Please report to dev)"
            # Error handler (just in case)
            
            match missing_stat:
                case "overall ranking":
                    selector = "span.Villain__RankingSpan-sc-8s66oj-4.fDSmVR > span"
                    tag_text = college_soup.select(selector)[0].getText()[1:]
                    if not tag_text.isdigit(): tag_text = "N/A"
                case "location":
                    selector = "span.NuggetsContainer__LocationSpan-sc-108otk5-0.GXzCk.mr2"
                    tag_text = college_soup.select(selector)[0].getText()
                    tag_text = tag_text[tag_text.find("•")+2:]
                    state_portion = tag_text[-2:]
                    try:
                        tag_text = tag_text.replace(state_portion, state_abbreviations.state_abbreviations_dict[state_portion])
                    except KeyError:
                        tag_text = "N/A"
                case "setting":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[0].getText()
                    if not tag_text.lower() in ["city", "urban", "suburban", "rural"]: tag_text = "N/A"
                case "school population":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[2].getText()
                    if not (tag_text[0].isdigit() and tag_text[-1].isdigit()): tag_text = "N/A"                        
                case "acceptance":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[3].getText()
                    if tag_text[-1] != "%": tag_text = "N/A"
                case "sat":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[4].getText()
                    if "-" not in tag_text: tag_text = "N/A"
                case "act":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[5].getText()
                    if "-" not in tag_text: tag_text = "N/A"
                case "gpa":
                    selector = "p.Paragraph-sc-1iyax29-0.kqzqfx"
                    tag_text = college_soup.select(selector)[6].getText()
                    if "." not in tag_text: tag_text = "N/A"
            return tag_text
        
        
        # Fetch result page for college
#         print(f"Fetching result page for {self.name}...")
        results_page = requests.get("https://www.usnews.com/search?q=" + self.name, headers =  newheaders)
        results_page.raise_for_status()
        results_soup = BeautifulSoup(results_page.text, "html.parser")
        
        # Fetch page for college
#         print(f"Fetching page for {self.name}...")
        first_result_tag = results_soup.select("a.Anchor-byh49a-0.MediaObjectBox__AnchorWrap-sc-7ytr6b-5.eMEqFO.bbyhFG")[0]
        college_page = requests.get(first_result_tag.get("href"), headers = newheaders)
        college_page.raise_for_status()
        college_soup = BeautifulSoup(college_page.text, "html.parser")
        
        # Fill unfilled cells
        for unfilled_cell in self.unfilled_cells:
            unfilled_stat_header = key_columns[unfilled_cell]
            try:
                self.row[unfilled_cell] = get_stat(unfilled_stat_header, college_soup)
            except IndexError as Error:
                self.row[unfilled_cell] = f"Error: {Error}"
            # Error handler
        

def main():
    college_sheet_obj = college_sheet(confiq.spreadsheet_id)
    college_sheet_obj.generate_key_columns(confiq.FIELDS)
    college_sheet_obj.get_unfilled_college_rows()
    college_sheet_obj.fill_unfilled_colleges()
    college_sheet_obj.upload_spreadsheet()
    
if __name__ == "__main__":
    try:
        main()
    except JSONDecodeError as Error:
        print(f"{Error}: Try again!")
    # Error handler   
