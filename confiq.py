spreadsheet_id = "<INSERT SPREADSHEET ID/LINK HERE>" # Main sheet


# Replace <INSERT SPREADSHEET ID/LINK HERE> with 
# your spreadsheet's ID/LINK
# example: spreadsheet_id = "1XZ4ruaR8mLOJIi7PIUvorb1BPy9tu1-M963MpIFO6lA"
# Remember to keep the quotes ("")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Only change keys, do NOT change values !!
# WARNING: write everything in LOWERCASE and wrap words in quotation marks
FIELDS = {
    "school population": "school population",
    "location": "location",
    "overall ranking": "overall ranking",
    "institution type": "institution type",
    "setting": "setting",
    "acceptance rate": "acceptance",
    "sat range": "sat",
    "act range": "act",
    "high school gpa": "gpa"
}

# Default template
'''
FIELDS = {
    "school population": "school population",
    "location": "location",
    "overall ranking": "overall ranking",
    "institution type": "institution type",
    "setting": "setting",
    "acceptance": "acceptance",
    "sat": "sat",
    "act": "act",
    "gpa": "gpa"
}
'''
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Prevent blocking
newheaders = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux i686 on x86_64)'
#     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
}