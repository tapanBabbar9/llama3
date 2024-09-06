from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, FileResponse
from datetime import timedelta
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
    {"title": "VALLEY OF THE DOLLS", "author": "Jacqueline Susann"},
    {"title": "9 1/2 Weeks", "author": "Judith Viola"},
    {"title": "Willy Wonka", "author": "Roald Dahl"},
    {"title": "The Way We Were", "author": "Arthur Laurents"},
    {"title": "The Portable Dorothy Parker", "author": "Dorothy Parker"},
    {"title": "Metamorphosis", "author": "Kafka"},
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

def convert_timestamp(timestamp):
    # Remove the trailing 't' and convert to an integer
    milliseconds = int(timestamp[:-1])
    
    # Convert milliseconds to seconds
    seconds = milliseconds / 1000
    
    # Convert seconds to a timedelta object
    time_delta = timedelta(seconds=seconds)
    
    # Extract hours and minutes from the timedelta object
    total_seconds = int(time_delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    # Format as hh:mm
    return f"{int(hours):02}:{int(minutes):02}"

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
            dialogue = root.findall(".//ttml:p", namespaces)
            for idx, elem in  enumerate(dialogue):
                text = elem.text
                if text is not None and query.lower() in text.lower():
                    # Extract the necessary attributes
                    begin = elem.get('begin')
                    # Initialize the result dictionary
                    result = {
                        'file': file_name,
                        'begin': convert_timestamp(begin),
                        'text': dialogue[idx].text if dialogue[idx].text is not None else ''
                    }

                    # Check if there is a previous dialogue element and .text exists
                    if idx > 0 and dialogue[idx - 1].text is not None:
                        result['text'] = dialogue[idx - 1].text + " " + result['text']

                    # Check if there is a next dialogue element and .text exists
                    if idx < len(dialogue) - 1 and dialogue[idx + 1].text is not None:
                        result['text'] += " " + dialogue[idx + 1].text
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
