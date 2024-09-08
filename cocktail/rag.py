import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_community.embeddings import OllamaEmbeddings
import ollama

# Initialize PgVector with SQLAlchemy
engine = create_engine('postgresql://postgres:@localhost:5432/db_name')

# Initialize the embedding model (using Ollama Llama 3)
ollama_emb = OllamaEmbeddings(model="llama3")


# Streamlit UI
st.title("AI Bartender Chat")
user_query = st.text_input("Ask me for cocktail suggestions:")

# Dropdown for selecting a character
character_options = [
    "Batman",
    "Gandhi",
    "Marilyn Monroe",
    "Albert Einstein",
    "Sherlock Holmes",
    "Mickey Mouse",
    "Cleopatra",
    "Charlie Chaplin",
    "Homer Simpson",
    "Mona Lisa",
    "James Bond",
    "Rick Sanchez",
    "Dracula",
    "Victor Frankenstein's Monster",
    "Virginia Woolf",    
]
character = st.selectbox("Choose your AI bartender character:", character_options)


if user_query:
    # Generate embedding for the user's query
    query_embedding = ollama_emb.embed_query(user_query)

    # Convert the embedding into a PostgreSQL-compatible string (ARRAY[...])
    embedding_str = f"ARRAY[{', '.join(map(str, query_embedding))}]"

    # SQL query with proper type casting
    sql_query = f"""
        SELECT cocktail_name, bartender, bar_company, location, ingredients, garnish, glassware, preparation, notes
        FROM cocktail_recipes
        ORDER BY embedding <-> {embedding_str}::vector
        LIMIT 5;
    """

    # Execute the query and fetch results
    with engine.connect() as connection:
        result = connection.execute(text(sql_query))
        rows = result.fetchall()
        df = pd.DataFrame(rows, columns=["Cocktail Name", "Bartender", "Bar/Company", "Location", "Ingredients", "Garnish", "Glassware", "Preparation", "Notes"])
    print(df)
    # Construct the prompt for LLaMA 3
    if not df.empty:
        context = ""
        for _, row in df.iterrows():
            context += (
                f"Cocktail Name: {row['Cocktail Name']}\n"
                f"Bartender: {row['Bartender']}\n"
                f"Bar/Company: {row['Bar/Company'] if pd.notna(row['Bar/Company']) else 'Unknown'}\n"
                f"Location: {row['Location'] if pd.notna(row['Location']) else 'Unknown'}\n"
                f"Ingredients: {row['Ingredients']}\n"
                f"Garnish: {row['Garnish'] if pd.notna(row['Garnish']) else 'None'}\n"
                f"Glassware: {row['Glassware'] if pd.notna(row['Glassware']) else 'Not specified'}\n"
                f"Preparation: {row['Preparation']}\n"
                f"Notes: {row['Notes'] if pd.notna(row['Notes']) else 'None'}\n\n"
            )

        prompt = f"""
        You are {character} who is working as a professional bartender. Based on the following cocktail recipes, respond to the user's query with the best recommendations:

        {context}

        User Query: {user_query}
        
        Please provide a conversational response with your suggestions.
        """

        # Generate a response using LLaMA 3
        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response['message']['content'].strip()
        st.write(response_text)
    else:
        st.write("Sorry, I couldn't find any cocktails matching your query.")
