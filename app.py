import pandas as pd
import streamlit as st

st.title('Infrastructure Pipeline Dashboard')


    
def clean_billions(text):
    if 'Billion' in text:
        text = text.strip(' Billion')
        text = text.replace('.', ',')
        text += '00,000,000'
    return text

def clean_numeric(text):
    new_text = clean_billions(text)
    new_text = new_text.replace(',', '')
    return new_text

def clean_cost(data):
    data['Cost'] = data['Cost'].str.strip('$').replace('?', '0')
    data['Cost'] = data.Cost.apply(clean_numeric).astype('float')
    return data

def load_data():
    df = pd.read_csv('./data.csv')
    df.columns = df.columns.str.strip(' ')
    return clean_cost(df)
    
data = load_data()
st.subheader('Raw Data')
st.write(data)
