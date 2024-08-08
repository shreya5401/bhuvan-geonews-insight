import os
import json
import re
import string
import numpy as np
import pandas as pd
import psycopg2
import tensorflow as tf
from tensorflow.keras.preprocessing import text as keras_text
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Dropout
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Function to clean text
def clean_text(txt):
    contraction_dict = {"ain't": "is not", "aren't": "are not", "can't": "cannot", 
                        "'cause": "because", "could've": "could have", 
                        "couldn't": "could not", "didn't": "did not",  
                        "doesn't": "does not", "don't": "do not", "hadn't": "had not", 
                        "hasn't": "has not", "haven't": "have not", 
                        "he'd": "he would", "he'll": "he will", "he's": "he is", 
                        "how'd": "how did", "how'd'y": "how do you", "how'll": "how will", 
                        "how's": "how is",  "I'd": "I would", "I'd've": "I would have", 
                        "I'll": "I will", "I'll've": "I will have", "I'm": "I am", 
                        "I've": "I have", "i'd": "i would", "i'd've": "i would have", 
                        "i'll": "i will",  "i'll've": "i will have", "i'm": "i am", 
                        "i've": "i have", "isn't": "is not", "it'd": "it would", 
                        "it'd've": "it would have", "it'll": "it will", 
                        "it'll've": "it will have", "it's": "it is", "let's": "let us", 
                        "ma'am": "madam", "mayn't": "may not", "might've": "might have",
                        "mightn't": "might not", "mightn't've": "might not have", 
                        "must've": "must have", "mustn't": "must not", 
                        "mustn't've": "must not have", "needn't": "need not", 
                        "needn't've": "need not have", "o'clock": "of the clock", 
                        "oughtn't": "ought not", "oughtn't've": "ought not have", 
                        "shan't": "shall not", "sha'n't": "shall not", 
                        "shan't've": "shall not have", "she'd": "she would", 
                        "she'd've": "she would have", "she'll": "she will", 
                        "she'll've": "she will have", "she's": "she is", 
                        "should've": "should have", "shouldn't": "should not", 
                        "shouldn't've": "should not have", "so've": "so have",
                        "so's": "so as", "this's": "this is", "that'd": "that would", 
                        "that'd've": "that would have", "that's": "that is", 
                        "there'd": "there would", "there'd've": "there would have", 
                        "there's": "there is", "here's": "here is",
                        "they'd": "they would", "they'd've": "they would have", 
                        "they'll": "they will", "they'll've": "they will have", 
                        "they're": "they are", "they've": "they have", 
                        "to've": "to have", "wasn't": "was not", "we'd": "we would", 
                        "we'd've": "we would have", "we'll": "we will", 
                        "we'll've": "we will have", "we're": "we are", 
                        "we've": "we have", "weren't": "were not", 
                        "what'll": "what will", "what'll've": "what will have", 
                        "what're": "what are",  "what's": "what is", 
                        "what've": "what have", "when's": "when is", 
                        "when've": "when have", "where'd": "where did", 
                        "where's": "where is", "where've": "where have", 
                        "who'll": "who will", "who'll've": "who will have",
                        "who's": "who is", "who've": "who have", "why's": "why is", 
                        "why've": "why have", "will've": "will have", 
                        "won't": "will not", "won't've": "will not have", 
                        "would've": "would have", "wouldn't": "would not", 
                        "wouldn't've": "would not have", "y'all": "you all", 
                        "y'all'd": "you all would", "y'all'd've": "you all would have",
                        "y'all're": "you all are", "y'all've": "you all have",
                        "you'd": "you would", "you'd've": "you would have", 
                        "you'll": "you will", "you'll've": "you will have", 
                        "you're": "you are", "you've": "you have"}

    def _get_contractions(contraction_dict):
        contraction_re = re.compile('(%s)' % '|'.join(contraction_dict.keys()))
        return contraction_dict, contraction_re

    def replace_contractions(text):
        contractions, contractions_re = _get_contractions(contraction_dict)
        def replace(match):
            return contractions[match.group(0)]
        return contractions_re.sub(replace, text)

    # replace contractions
    txt = replace_contractions(txt)
    
    # remove punctuations
    txt = "".join([char for char in txt if char not in string.punctuation])
    txt = re.sub('[0-9]+', '', txt)
    
    # split into words
    words = word_tokenize(txt)
    
    # remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]
    
    # removing leftover punctuations
    words = [word for word in words if word.isalpha()]
    
    cleaned_text = ' '.join(words)
    return cleaned_text

# Load the saved tokenizer
tokenizer_file = r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Text Classification\model_files\tokenizer.json'
with open(tokenizer_file, 'r') as f:
    tokenizer_data = json.load(f)

# Convert dictionary back to JSON string
tokenizer_json = json.dumps(tokenizer_data)
tokenizer = keras_text.tokenizer_from_json(tokenizer_json)

# Load the saved embedding matrix
embedding_matrix_file = r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Text Classification\model_files\embedding_matrix.npy'
embedding_matrix = np.load(embedding_matrix_file)

# Recreate the LSTM model architecture
vocab_len = embedding_matrix.shape[0]
emb_dim = embedding_matrix.shape[1]
max_len = 300  # Maximum length of sequences

lstm_model = Sequential()
lstm_model.add(Embedding(vocab_len, emb_dim, trainable=False, weights=[embedding_matrix]))
lstm_model.add(LSTM(128, return_sequences=False))
lstm_model.add(Dropout(0.5))
lstm_model.add(Dense(1, activation='sigmoid'))
lstm_model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Build the model by passing a dummy input
lstm_model.build(input_shape=(None, max_len))

# Load the saved model weights
model_weights_file = r'C:\Users\shrey\OneDrive\Desktop\Projects\GeoSpace News\ISRO BHUMI\Text Classification\model_files\lstm_model.weights.h5'
lstm_model.load_weights(model_weights_file)

# PostgreSQL connection parameters
db_params = {
    "host": "localhost",
    "database": "news",
    "user": "postgres",
    "password": "shiro123"
}

# Establish a connection to PostgreSQL
conn = psycopg2.connect(**db_params)

# Check if the table exists, and create it if not
with conn.cursor() as cursor:
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='scraped_db') THEN
            CREATE TABLE scraped_db(
                id SERIAL PRIMARY KEY,
                content TEXT,
                sentiment INTEGER
            );
        END IF;
    END
    $$;
    """)

# Check if the 'sentiment' column exists, and create it if not
with conn.cursor() as cursor:
    cursor.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='scraped_db' AND column_name='sentiment') THEN
            ALTER TABLE scraped_db ADD COLUMN sentiment INTEGER;
        END IF;
    END
    $$;
    """)

# Function to predict sentiment and update database
def predict_sentiment_and_update_db():
    # Fetch the content from the table
    with conn.cursor() as cursor:
        cursor.execute('SELECT id, content FROM scraped_db WHERE sentiment IS NULL')  # Only fetch rows where sentiment is NULL
        rows = cursor.fetchall()
    
    # Iterate through each row and update sentiment
    for row in rows:
        # Clean and preprocess the text
        cleaned_text = clean_text(row[1])
        
        # Tokenize and pad the sequence
        sequence_data = tokenizer.texts_to_sequences([cleaned_text])
        padded_sequence_data = sequence.pad_sequences(sequence_data, maxlen=max_len)
        
        # Predict sentiment
        sentiment_prediction = lstm_model.predict(padded_sequence_data)[0][0]
        
        # Convert sentiment prediction to integer (0 or 1)
        rounded_sentiment = int(sentiment_prediction > 0.5)
        
        # Update database with rounded sentiment prediction
        with conn.cursor() as cursor:
            cursor.execute('UPDATE scraped_db SET sentiment = %s WHERE id = %s', (rounded_sentiment, row[0]))
    
    # Commit the transaction
    conn.commit()

# Example usage:
predict_sentiment_and_update_db()

# Close the connection
conn.close()

print("Sentiment values (rounded and converted to integer) updated in the database.")
