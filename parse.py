apiKey = "YOUR_API_KEY_HERE"

from src.NameParser.generate import clsGenerateNames

try:
    names = clsGenerateNames(apiKey)
    if(names.generate(5)):
        for name in names._list:
            print(name) #Returns five random names.
            details=names.details(name) #Returns all details we have on the generated name.
except:
    print("An exception occurred")
