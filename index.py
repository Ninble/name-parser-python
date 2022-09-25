# These classes hold all functionality.
from src.NameParser.extract import clsExtractNames
from src.NameParser.generate import clsGenerateNames
from src.NameParser.parse import clsParseName

# Get your API key on https://parser.name/
apiKey = "Your-API-Key-Here"

# Initialize the class that parses names.
name = clsParseName(apiKey)

# Parse a complete name.
if (name.fromCompleteName("Linus Benedict Torvalds")):
    print(name._gender) #Returns "m".

# Parse an email address.
if(name.fromEmailAddress("linus.torvalds@protonmail.org")):
    print(name._salutation) #Returns "Mr.".
    print(name._firstname) #Returns "Linus".
    print(name._lastname) #Returns "Torvalds".
    print(name._gender)   #Returns "m".

# Validate a name
if(name.validate("random_mnbas")):
    print(name.valid()) #Returns "bool(false)".

# Initialize the class that generates names.
names = clsGenerateNames(apiKey)

# Generate five random name.
if(names.generate(5)):
    for name in names._list:
        print(name) #Returns five random names.
        details=names.details(name) #Returns all details we have on the generated name.

# Initialize the class that extracts names.
names = clsExtractNames(apiKey)

# Extract names from text.
if(names.extract("Veteran quarterback Philip Rivers moved ahead of Matteo Federica on the NFL's all-time passing list.")):
    for name in names._list:
        print(name) #Returns "Philip Rivers" and "Matteo Federica".
        details=names.details(name) #Returns all data we have on the extracted name.