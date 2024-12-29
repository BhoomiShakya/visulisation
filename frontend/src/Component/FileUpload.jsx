import React, { useState } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import Plotly from "plotly.js/dist/plotly.min.js";
import ChartDisplay from './ChartDisplay'; // Import the ChartDisplay component

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [query, setQuery] = useState('');
    const [charts, setCharts] = useState({});
    const [resultMessage, setResultMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleQuerySubmit = async () => {
        if (!file || !query) return alert('Please upload a file and enter a query.');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('query', query);
        console.log("formData file",file )
        console.log("formData query ",query )
        try {
            const response = await axios.post('http://localhost:8000/query', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            console.log("response hu mein",response)
            if (response.data) {
                setCharts(response.data.charts || []);
                console.log("response data mein hu",response.data.charts)
                setResultMessage(response.data.message || '');
                console.log("response data message hu",response.data.message)

            } else {
                console.error('No response data received:', response);
            }
        } catch (error) {
            console.error('Error processing query:', error);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4">
            <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-6 space-y-6">
                {/* File Upload Section */}
                <div className="space-y-4">
                    <label className="block">
                        <span className="text-gray-700">Upload File</span>
                        <input
                            type="file"
                            accept=".csv, .xlsx"
                            onChange={handleFileChange}
                            className="mt-2 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700"
                        />
                    </label>
                    <textarea
                        placeholder="Ask a question about the data..."
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        className="w-full h-32 p-4 border rounded-md focus:outline-none focus:ring focus:ring-blue-300"
                    />
                    <button
                        onClick={handleQuerySubmit}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
                    >
                        Submit Query
                    </button>
                </div>


                {/* ChartDisplay Component */}
                <ChartDisplay charts={charts} resultMessage={resultMessage} />
            </div>
        </div>
    );
};

export default FileUpload;
