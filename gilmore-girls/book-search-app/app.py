from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
import os
import xml.etree.ElementTree as ET

app = FastAPI()

# Path to the folder containing XML files
XML_FOLDER = './static'

# Serve the HTML front-end
@app.get("/")
async def serve_frontend():
    return FileResponse("templates/index.html")

# List of books after removing duplicates
books = [
    {"title": "Huckleberry Finn", "author": "Mark Twain"},
    {"title": "Moby Dick", "author": "Herman Melville"},
    {"title": "Madame Bovary", "author": "Gustave Flaubert"},
    {"title": "The Little Match Girl", "author": "Hans Christian Andersen"},
    {"title": "Peyton Place", "author": "Richard Peabody Simmons"},
    {"title": "Gaucho", "author": "Jorge Luis Borges"},
    {"title": "TO PERM OR NOT TO PERM", "author": "William Shakespeare (as Hamlet)"},
    {"title": "VALLEY OF THE DOLLS", "author": "Jacqueline Susann"},
    {"title": "Mushrooms", "author": "Lewis Carroll"},
    {"title": "9 1/2 Weeks", "author": "Judith Viola"},
    {"title": "Willy Wonka", "author": "Roald Dahl"},
    {"title": "The Way We Were", "author": "Arthur Laurents"},
    {"title": "Beloved", "author": "Toni Morrison"},
    {"title": "Pride and Prejudice", "author": "Jane Austen"},
    {"title": "The Portable Dorothy Parker", "author": "Dorothy Parker"},
    {"title": "Alice in Wonderland", "author": "Lewis Carroll"},
    {"title": "The Gift of the Magi", "author": "O. Henry"},
    {"title": "Metamorphosis", "author": "Kafka"},
    {"title": "A Christmas Carol", "author": "Charles Dickens"},
    {"title": "A Tale of Two Cities", "author": "Charles Dickens"},
    {"title": "Great Expectations", "author": "Charles Dickens"},
    {"title": "Little Dorrit", "author": "Charles Dickens"},
    {"title": "David Copperfield", "author": "Charles Dickens"},
    {"title": "War and Peace", "author": "Leo Tolstoy"},
    {"title": "Anna Karenina", "author": "Leo Tolstoy"},
    {"title": "The Shining", "author": "Stephen King"},
    {"title": "Richard III", "author": "William Shakespeare"},
    {"title": "The Sonnets", "author": "William Shakespeare"},
    {"title": "Schindler's List", "author": "Thomas Keneally"},
    {"title": "Mencken's Chrestomathy", "author": "H.L. Mencken"},
    {"title": "Midnight Express", "author": "Dalton Trumbo"},
    {"title": "The Outsiders", "author": "S.E. Hinton"},
    {"title": "To Cotillion", "author": "Jane Austen"},
    {"title": "Barron's", "author": "Walter Burley Griffin"},
]



@app.get("/books")
def get_books():
    return {"books": books}

# Function to search for books in the XML files
def search_books_in_xml(query: str):
    results = []
    # Define the namespace from the XML file
    namespaces = {'ttml': 'http://www.w3.org/ns/ttml'}

    print(XML_FOLDER)
    # Loop through all XML files in the directory
    for file_name in os.listdir(XML_FOLDER):
        if file_name.endswith(".xml"):
            file_path = os.path.join(XML_FOLDER, file_name)
            
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            print(f"Searching in {file_name}")
            print(root)
            # Search for the query in the text content of each <p> tag
            for elem in root.findall(".//ttml:p", namespaces):
                text = elem.text
                if text is not None and query.lower() in text.lower():
                    # Extract the necessary attributes
                    begin = elem.get('begin')
                    result = {
                        'file': file_name,
                        'begin': begin,
                        'text': text
                    }
                    results.append(result)
    
    return results

# API endpoint to search books
@app.get("/search/")
async def search_books(query: str = Query(..., description="The book keyword to search")):
    print(f"Searching for books with keyword: {query}")
    results = search_books_in_xml(query)
    if results:
        return JSONResponse(content=results)
    else:
        return JSONResponse(content={"message": "No results found."})

# Run the server with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
