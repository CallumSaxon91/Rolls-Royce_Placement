# Spacy Research

### Introduction
This project is our experimentation with the Spacy python package. Essentially we combined this module with the Tkinter module to create a desktop app.

## What the desktop app does
The desktop app, when ran, allows a user to enter a link to a wikipedia page. There is validation to ensure that the link inputted is a wikipedia link. Then once the "Search" button is clicked with a correct link in the input slot. The module then will scan the web page using AI and read all of the text that are in HTML "p" tags. The module will then scan through all of the texts from the "p" tags and store them as a string for analysis. 

The Spacy module will then scan through all the text in the string and print out several different entities that it found and it will also label them. For example, when the python programming module is entered and scanned. Guido van Rossum is identified as a person and 2000 is identified as a date. There are several different entities that can be identified. The list is stated below.

Also the dekstop app will count the number of verbs and nouns within the "p" tags that the Spacy module has identified.

## List of entities in the Spacy module
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

## Future plans for Development
From reading the NLP text extract here  we decided that we could make the following changes:

(Expression Recognition) 

From the text extract we decided we could incorporate a use of the days of the week enhancement, this would mean the spacy module would not only recognise numerical values as times, but also instead be able to recognise full expressions such as “the day after tomorrow” and days of the week such as “Friday” and “Monday”. This type of information would be useful to analyse when events are noted to have occurred throughout data sets and information. 

 

(Data Trees for Analysis) 

Something else we will be working on is the implementation of data trees, this additional feature will come in handy when identifying linked and more key significant events. This data tree will also allow us as a team to determine the effects of the linked events throughout topics and data sets. It will also be interesting to see how far the data tree will grow due to the predicted continuous data links and events. 

 

Experimental Plans 

(Wiki Explore) 

An experimental implementation	we have been planning is the links to other wiki pages. This implementation is to see the effects of how far wiki pages go out of the topics range. Our prediction of this is that the wiki topics will eventually become out of context to the first search and a bundle of data will be collected. 
