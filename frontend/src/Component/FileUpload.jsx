import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Plot from 'react-plotly.js';
import Plotly from "plotly.js/dist/plotly.min.js";

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [charts, setCharts] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(50); // Number of items to display per page
    const [searchQuery, setSearchQuery] = useState('');
    
    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (!file) return alert('Please upload a file.');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
            });
            console.log("response from chart", response);
            if (response.data && response.data.charts) {
                setCharts(Object.values(response.data.charts)); // Ensure charts are extracted correctly
            } else {
                console.error('No charts data received:', response.data);
            }
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
        setCurrentPage(1); // Reset to the first page on new search
    };

    // Filtering charts based on search query
    const filteredCharts = charts.filter(chart => 
        JSON.stringify(chart).toLowerCase().includes(searchQuery.toLowerCase())
    );

    // Pagination logic
    const indexOfLastItem = currentPage * itemsPerPage;
    const indexOfFirstItem = indexOfLastItem - itemsPerPage;
    const currentCharts = filteredCharts.slice(indexOfFirstItem, indexOfLastItem);

    const paginate = (pageNumber) => setCurrentPage(pageNumber);

    // Generate page numbers
    const pageNumbers = [];
    for (let i = 1; i <= Math.ceil(filteredCharts.length / itemsPerPage); i++) {
        pageNumbers.push(i);
    }

    return (
        <div>
            <input type="file" accept=".csv, .xlsx" onChange={handleFileChange} />
            <button onClick={handleFileUpload}>Upload</button>

            {/* Search bar */}
            <input 
                type="text" 
                placeholder="Search charts..." 
                value={searchQuery} 
                onChange={handleSearchChange} 
            />

            <div>
                {currentCharts.map((chart, index) => (
                    <Plot
                        key={index}
                        data={JSON.parse(chart).data}
                        layout={JSON.parse(chart).layout}
                    />
                ))}
            </div>

            {/* Pagination controls */}
            <div>
                <ul>
                    {pageNumbers.map(number => (
                        <li key={number} style={{ display: 'inline', margin: '0 5px' }}>
                            <button onClick={() => paginate(number)}>
                                {number}
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default FileUpload;
