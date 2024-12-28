from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import base64
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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
        
        charts = {}
         # Example 1: Bar chart (for categorical data)
        # if df.select_dtypes(include=['object']).columns.size > 0:
        #     categorical_col = df.select_dtypes(include=['object']).columns[0]
        #     bar_chart = px.bar(df, x=categorical_col, title=f"Bar Chart of {categorical_col}")
        #     charts["bar_chart"] = bar_chart.to_json()

        # # Example 2: Scatter plot (for numerical data)
        # if df.select_dtypes(include=['number']).columns.size >= 2:
        #     numerical_cols = df.select_dtypes(include=['number']).columns
        #     scatter_plot = px.scatter(df, x=numerical_cols[0], y=numerical_cols[1], title="Scatter Plot")
        #     charts["scatter_plot"] = scatter_plot.to_json()

        # # Example 3: Histogram
        # if df.select_dtypes(include=['number']).columns.size > 0:
        #     numeric_col = df.select_dtypes(include=['number']).columns[0]
        #     histogram = px.histogram(df, x=numeric_col, nbins=20, title=f"Histogram of {numeric_col}")
        #     charts["histogram"] = histogram.to_json()

        # # Example 4: Line chart (if there is time-series data)
        # if 'date' in df.columns:
        #     df['date'] = pd.to_datetime(df['date'], errors='coerce')
        #     df = df.dropna(subset=['date'])
        #     line_chart = px.line(df, x='date', y=numerical_cols[0], title="Line Chart over Time")
        #     charts["line_chart"] = line_chart.to_json()

        # return {"charts": charts}
        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            for col in numeric_cols:
                histogram = px.histogram(df, x=col, nbins=20, title=f"Histogram of {col}")
                charts[f"histogram_{col}"] = histogram.to_json()

                box_plot = px.box(df, y=col, title=f"Box Plot of {col}")
                charts[f"boxplot_{col}"] = box_plot.to_json()

        # Categorical and Numeric Relationship
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for cat_col in categorical_cols:
            for num_col in numeric_cols:
                bar_chart = px.bar(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
                charts[f"bar_{cat_col}_{num_col}"] = bar_chart.to_json()

                box_plot = px.box(df, x=cat_col, y=num_col, title=f"{num_col} Distribution by {cat_col}")
                charts[f"boxplot_{cat_col}_{num_col}"] = box_plot.to_json()

        # Categorical Distribution
        for cat_col in categorical_cols:
            pie_chart = px.pie(df, names=cat_col, title=f"Distribution of {cat_col}")
            charts[f"pie_{cat_col}"] = pie_chart.to_json()

        return {"charts": charts}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)