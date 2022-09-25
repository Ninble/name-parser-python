apiKey = "e05666adff6288e4a1e425e0c47f2e64"

from src.NameParser.generate import clsGenerateNames

try:
    names = clsGenerateNames(apiKey)
    if(names.generate(5)):
        for name in names._list:
            print(name) #Returns five random names.
            details=names.details(name) #Returns all details we have on the generated name.
except:
    print("An exception occurred")