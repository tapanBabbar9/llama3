import streamlit as st
import ollama
from sqlalchemy import create_engine, text
import whisper
import sounddevice as sd
import numpy as np
import tempfile
import os
import wave
import json

# Initialize Whisper model
whisper_model = whisper.load_model("turbo")

# Set up database connection
engine = create_engine('postgresql://postgres:password@localhost/postgres')

houses = {
    "Gryffindor": "images/Gryffindor_ClearBG.png",
    "Hufflepuff": "images/Hufflepuff_ClearBG.png",
    "Ravenclaw": "images/RavenclawCrest.png",
    "Slytherin": "images/Slytherin_ClearBG.png",
}


# Function to convert text to SQL using Ollama (text-to-SQL model)
def text_to_sql(natural_language_text):
    table_schemas = """
    house_points(house_name TEXT PRIMARY KEY, points INTEGER)
    """
    
    prompt_template = f"""
    You are a SQL expert.
    
    Please help to convert the following natural language command into a valid UPDATE SQL query. Your response should ONLY be based on the given context and follow the response guidelines and format instructions.

    ===Tables
    {table_schemas}

    ===Response Guidelines
    1. If the provided context is sufficient, please generate a valid query WITHOUT any explanations for the question.
    2. Please format the query before responding.
    3. Please always respond with a valid well-formed JSON object with the following format
    4. There are only UPDATE queries and points are either added or deducted from a house.

    ===Response Format
    {{
        "query": "A valid UPDATE SQL query when context is sufficient."
    }}

    ===Command
    {natural_language_text}
    """
    
    # Request SQL conversion from Ollama
    response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt_template}]
        )
    
    response_content = response['message']['content']
    
    try:
        response_json = json.loads(response_content)
        if "query" in response_json:
            return response_json["query"]
        else:
            return f"Error: {response_json.get('explanation', 'No explanation provided.')}"
    except json.JSONDecodeError:
        return "Error: Failed to parse response as JSON."


# Function to execute SQL queries using SQLAlchemy
def run_sql_query(query):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            conn.commit()
            return result
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None


# Function to record audio from the microphone and save it as a WAV file
def record_audio(duration, sample_rate=16000):
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_wav.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)   # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes(np.int16(audio_data * 32767))  # Convert float32 to int16
    
    return temp_wav.name

# Function to transcribe audio using Whisper
def audio_to_text_from_mic(duration=5):
    audio_file = record_audio(duration)
    result = whisper_model.transcribe(audio_file)
    os.remove(audio_file)  # Clean up temp file
    return result['text']

# Streamlit App
st.title("Hogwarts House Points Tracker")

# Display current house points
def display_house_points():
    house_points_query = "SELECT * FROM house_points ORDER BY house_name"
    house_points = run_sql_query(house_points_query)

    # Create a grid layout with 4 columns
    cols = st.columns(4)  # Create 4 columns
    for index, (house, points) in enumerate(house_points):
        col = cols[index % 4]  # Get the appropriate column based on index
        with col:
            st.image(houses[house], use_column_width=True)  # Display the flag image
            st.markdown(f"<h5 style='text-align: center;'>{house}</h3>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center;'>{points} points</h3>", unsafe_allow_html=True)


# Record button for microphone input
if st.button("Record Command"):
    with st.spinner("Recording..."):
        transcribed_text = audio_to_text_from_mic(duration=5)
        print("Transcribed Text:", transcribed_text)

        # Convert transcribed text to SQL query
        sql_query = text_to_sql(transcribed_text)
        print("Generated SQL Query:", sql_query)

        # Execute the generated SQL query
        if sql_query and not sql_query.startswith("Error"):
            run_sql_query(sql_query)
            st.success("House points updated successfully!")
            #display_house_points()
        else:
            st.error("Failed to generate a valid SQL query.")
st.title("")
display_house_points()

