# These classes hold all functionality.
from src.NameParser.generate import clsGenerateNames
from src.NameParser.parse import clsParseName

# Get your API key on https://parser.name/
apiKey = "Your-API-Key-Here"

# Initialize the class that parses names.
name = clsParseName(apiKey)

# Parse a complete name.
if name.fromCompleteName("Linus Benedict Torvalds"):
    print(name.gender())  # Returns "m".
    print(name.letter())  # Returns "Dear Mr. Torvalds".
    print(name.nameArea())  # Returns "Nordic".

# Parse a name with titles in German.
name.setLanguage("de")
if name.fromCompleteName("Prof. Dr. Klaus Schmidt"):
    print(name.letter())  # Returns "Sehr geehrter Herr Prof. Dr. Schmidt".
name.setLanguage("")

# Parse an email address.
if name.fromEmailAddress("linus.torvalds@protonmail.org"):
    print(name.salutation())  # Returns "Mr.".
    print(name.firstname())  # Returns "Linus".
    print(name.lastname())  # Returns "Torvalds".
    print(name.gender())  # Returns "m".

# Validate a name.
if name.validate("random_mnbas"):
    print(name.valid())  # Returns False.

# Initialize the class that generates names.
names = clsGenerateNames(apiKey)

# Generate five random names.
if names.generate(5):
    for generated in names.list():
        print(generated)  # Returns five random names.
        details = names.details(generated)  # Returns all details we have on the generated name.
