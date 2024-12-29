from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io
import plotly.graph_objects as go
import plotly.express as px
import duckdb
from fastapi.middleware.cors import CORSMiddleware
import requests
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyDTYzRuR1E_opeajPKKnbJmMjyUqhPq2ss")  # Replace with your actual Gemini API key
model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI()

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def requires_binning(column, threshold=10000):
    """Check if binning is needed based on the range of values in a numeric column."""
    return (column.max() - column.min()) > threshold

@app.post("/query")
async def process_query(file: UploadFile = File(...), query: str = Form(...)):
    try:
        # Read the uploaded file
        content = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            return JSONResponse(content={"error": "Unsupported file type"}, status_code=400)

        if df.empty:
            return JSONResponse(content={"error": "Uploaded file is empty"}, status_code=400)
        
        columns_list = list(df.columns)
        print("columns_list:", columns_list)
        table_name = file.filename  # Use the uploaded file name as the table name or customize as needed

        # Create a query structure for Gemini API
        modified_query = f"""
            give me an SQL query in text only on the basis of the user query for the following data '{df}' and table name {file.filename} with the following columns: {', '.join(columns_list)}. 
            The user query is: '{query}'.
            Please generate an appropriate SQL query to calculate summary statistics (e.g., average, min, max) for the columns mentioned in the query. 
            Ensure that the SQL query can handle the dataset's column names dynamically and return useful statistical information.
            no explanation . 
            """


        # Send query to Gemini API
        gemini_api_key = "AIzaSyDTYzRuR1E_opeajPKKnbJmMjyUqhPq2ss"  # Replace with your actual Gemini API key
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
        gemini_payload = {
            "contents": [
                {
                    "parts": [{"text": modified_query}]
                }
            ]
        }

        gemini_response = requests.post(
            gemini_url,
            headers={"Content-Type": "application/json"},
            json=gemini_payload
        )

        if gemini_response.status_code != 200:
            return JSONResponse(
                content={
                    "error": "Failed to generate SQL query",
                    "status_code": gemini_response.status_code,
                    "message": gemini_response.text
                },
                status_code=500
            )

        gemini_response_data = gemini_response.json()
        print("Gemini API Response:", gemini_response_data)  # Log the response data for debugging

        # Extract the generated SQL query
        sql_query = gemini_response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        # Remove Markdown code block markers if present
        if sql_query.startswith("```sql") and sql_query.endswith("```"):
            sql_query = sql_query[6:-3].strip()

        print("sql_query ------->>>>>",sql_query)

        if not sql_query:
            return JSONResponse(content={"error": "Generated SQL query is empty", "response":gemini_response_data}, status_code=500)
        
        # Register the DataFrame as a DuckDB table
        duckdb.register("df", df)
        # duckdb.sql(f"DROP TABLE IF EXISTS USA_Housing")
        # duckdb.sql("CREATE TABLE USA_Housing AS SELECT * FROM df")
        try:
            # Attempt to drop the table
            duckdb.sql(f"DROP TABLE IF EXISTS USA_Housing")
        except Exception as e:
            # Handle any errors that may occur during DROP
            print(f"Error dropping table: {e}")

        # Now, execute CREATE TABLE regardless of whether DROP was successful or not
        duckdb.sql("CREATE TABLE USA_Housing AS SELECT * FROM df")


        # Execute the SQL query using DuckDB
        result_df = duckdb.query(sql_query).df()

        charts = {}
        # Generate Dynamic Charts Based on Query Results
        if not result_df.empty:
            for column in result_df.columns:
                # Check if the column is numeric for creating indicator and bar charts
                if pd.api.types.is_numeric_dtype(result_df[column]):
                    # Generate Indicator Chart for numeric columns (using the first row's value)
                    value = result_df[column].iloc[0]
                    fig = go.Figure()
                    fig.add_trace(go.Indicator(
                        mode="number",
                        value=value,
                        title={"text": f"Indicator for {column}"},
                        number={'prefix': ""},  # Customize the number format as needed
                        domain={'x': [0, 1], 'y': [0, 1]}
                    ))
                    fig.update_layout(
                        font=dict(size=18),
                        font_color='blue',
                        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
                    )
                    charts[f"indicator_{column}"] = fig.to_json()

                    # Generate Bar Chart if the column is grouped
                    if len(result_df) > 1:
                        fig = px.bar(result_df, x=result_df.index, y=column, title=f"Bar Chart for {column}")
                        charts[f"bar_{column}"] = fig.to_json()

                    # Apply Binning to Numeric Data if required
                    if requires_binning(result_df[column]):
                        # Bin the data if the column's range exceeds the threshold
                        binning = pd.cut(result_df[column], bins=4)
                        fig = px.bar(x=binning.value_counts().index, y=binning.value_counts(), title=f"Binned Bar Chart for {column}")
                        charts[f"binned_{column}"] = fig.to_json()

                # Check if the column is categorical for creating pie charts
                elif pd.api.types.is_categorical_dtype(result_df[column]) or result_df[column].dtype == object:
                    # Generate Pie Chart for categorical columns
                    if len(result_df) > 1:
                        fig = px.pie(result_df, names=column, values=result_df.columns[1], title=f"Pie Chart for {column}")
                        charts[f"pie_{column}"] = fig.to_json()

        if not charts:
            return JSONResponse(content={"error": "No charts generated due to insufficient data"}, status_code=400)

        return JSONResponse(content={"charts": charts}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

