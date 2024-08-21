# US NEWS college spreadsheet updater
---
## Update your college google spreadsheet with information from US NEWS!
---
### Description
While making a college spreadsheet, filling out information like student population, school's ranking, acceptance rate and SAT score range can be tedious, especially when you have not narrowed down your list and have a large number of schools on your list. Conviniently, these types of information are readily available on US News college ranking, with a comprehensive database of colleges across the US. 

This program aims to convert the lengthy process into a single mouse click. It scrapes US News for the above types of information and quickly fills out your own college sheet when executed.

---
### Instructions
There are currently only instructions for Windows users
#### Installing Python
Download Python from its official website: https://www.python.org/downloads/
#### Installing python libraries
Run these commands in Terminal:
1. `pip install --user ezsheets`
2. `pip install --user BeautifulSoup4`
3. `pip install --user tqdm`
#### Creating the credential and tokens
##### Enabling Sheets API
1. Head to https://console.cloud.google.com/projectselector2/apis/library/sheets.googleapis.com
2. Click on "Select a project"
3. Click "New project"
4. Assign the project a name and click "Create"
5. Click "Enable"
##### Enabling Drive API
1. Head to https://console.cloud.google.com/projectselector2/apis/library/drive.googleapis.com
2. Select the same project and click "Enable"
##### Creating credentials
1. Head to https://console.cloud.google.com/
2. Click on the hamburger icon on the top-left corner
3. Hover mouse over "APIs and Services"
4. Click on "Enabled APIs and services"
5. Click on "Credentials on the left-side menu"
6. "CREATE CREDENTIALS" -> "OAuth client ID" -> "Configure Consent Screen"
7. Select "External" -> "Create"
8. Fill in the relevant information
9. Return to https://console.cloud.google.com/apis/credentials and download the credential under "OAuth 2.0 Client IDs"
##### Renewing the credential
Every time your credential expires, download a new one at https://console.cloud.google.com/apis/credentials

#### Configuring the settings
All configurations are made in the file confiq.py by editing the file with a text editor or IDE.

Replace "<INSERT SPREADSHEET ID/LINK HERE>" with your college spreadsheet's ID/LINK.

Replace text strings on the left side of the colon with the column headers on your college sheet. Do NOT change the text strings on the RIGHT side of the colon, those are used to determine what stats to track.

The "newheaders" variable on the bottom of the file is to prevent blocking from US NEWS. Only change if you are familiar with Python's "requests" module.
#### Executing the program
