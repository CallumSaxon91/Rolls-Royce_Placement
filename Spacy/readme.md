# Spacy Research

###Introduction
This project is our experimentation with the Spacy python package. Essentially we combined this module with the Tkinter module to create a desktop app.

##What the desktop app does
The desktop app, when ran, allows a user to enter a link to a wikipedia page. There is validation to ensure that the link inputted is a wikipedia link. Then once the "Search" button is clicked with a correct link in the input slot. The module then will scan the web page using AI and read all of the text that are in HTML "p" tags. The module will then scan through all of the texts from the "p" tags and store them as a string for analysis. 

The Spacy module will then scan through all the text in the string and print out several different entities that it found and it will also label them. For example, when the python programming module is entered and scanned. Guido van Rossum is identified as a person and 2000 is identified as a date. There are several different entities that can be identified. The list is stated below.

Also the dekstop app will count the number of verbs and nouns within the "p" tags that the Spacy module has identified.

##List of entities in the Spacy module
PERSON: People, including fictional.
NORP: Nationalities or religious or political groups.
FAC: Buildings, airports, highways, bridges, etc.
ORG: Companies, agencies, institutions, etc.
GPE: Countries, cities, states.
LOC: Non-GPE locations, mountain ranges, bodies of water.
PRODUCT: Objects, vehicles, foods, etc. (Not services.)
EVENT: Named hurricanes, battles, wars, sports events, etc.
WORK_OF_ART: Titles of books, songs, etc.
LAW: Named documents made into laws.
LANGUAGE: Any named language.
DATE: Absolute or relative dates or periods.
TIME: Times smaller than a day.
PERCENT: Percentage, including ”%“.
MONEY: Monetary values, including unit.
QUANTITY: Measurements, as of weight or distance.
ORDINAL: “first”, “second”, etc.
CARDINAL: Numerals that do not fall under another type.


