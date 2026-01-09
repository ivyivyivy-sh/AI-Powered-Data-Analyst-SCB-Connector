from google import genai
import pandas as pd
import requests
import json

# --- 1. EXISTING AI FUNCTIONS ---
def get_gemini_client(api_key):
    return genai.Client(api_key=api_key)

def clean_data_with_ai(api_key, df, user_instruction):
    client = get_gemini_client(api_key)
    columns = df.columns.tolist()
    sample = df.head(2).to_dict()
    prompt = f"""
    You are a Python Data Cleaner. 
    Dataset Columns: {columns}
    Sample Data: {sample}
    User Instruction: "{user_instruction}"
    Task: Write Python code to clean the dataframe 'df'.
    1. Assume 'df' exists. 2. Modifiy 'df' directly. 3. Return ONLY code.
    """
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    return clean_code_string(response.text)

def analyze_data_with_ai(api_key, df, query):
    client = get_gemini_client(api_key)
    columns = df.columns.tolist()
    dtypes = df.dtypes.astype(str).to_dict()
    prompt = f"""
    You are a Data Analyst using Plotly.
    Columns: {columns}
    Types: {dtypes}
    User Query: "{query}"
    Task: Write Python code.
    1. If plot requested: create Plotly fig named 'fig'.
    2. If value requested: save as 'result'.
    3. Use 'df'. Return ONLY code.
    """
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    return clean_code_string(response.text)

def generate_insights(api_key, df, query):
    client = get_gemini_client(api_key)
    summary = df.describe().to_string()
    prompt = f"""
    You are a Senior Business Analyst. 
    User Query: "{query}"
    Data Statistics: {summary}
    Task: Provide 3-bullet point summary of key insights. Professional, concise.
    """
    response = client.models.generate_content(model="gemini-2.5-flash-lite", contents=prompt)
    return response.text

def clean_code_string(code):
    if code.startswith("```"):
        code = code.strip().split("\n", 1)[1]
        if code.endswith("```"):
            code = code[:-3]
    return code.strip()

# --- 2. NEW SCB CONNECTOR FUNCTION ---
def fetch_scb_data(url, json_query_str):
    """
    Sends a JSON query to SCB and parses the response into a Pandas DataFrame.
    """
    try:
        # 1. Parse string input to JSON dict
        query_data = json.loads(json_query_str)

        # Robustness Fix: Force the format to always be 'json' . This prevents the error if the user accidentally copied "px" or "csv"
        if "response" not in query_data:
            query_data["response"] = {}
        query_data["response"]["format"] = "json"
        
        # 2. Send POST request
        response = requests.post(url, json=query_data)
        response.raise_for_status() # Check for errors
        
        # 3. Parse SCB Result (This is the tricky part)
        data = response.json()
        
        # Extract columns and data points
        columns = [col['text'] for col in data['columns']]
        data_rows = []
        
        for entry in data['data']:
            # SCB splits keys (regions/years) and values (numbers)
            row = entry['key'] + entry['values']
            data_rows.append(row)
            
        # 4. Create DataFrame
        df = pd.DataFrame(data_rows, columns=columns)
        
        # 5. Try to convert numeric columns automatically
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except:
                pass # Keep as text if it fails
                
        return df
        
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format. Please check your query syntax.")
    except Exception as e:
        raise Exception(f"Connection Failed: {e}")