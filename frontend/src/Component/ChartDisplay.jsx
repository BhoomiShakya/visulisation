import React from 'react';
import Plot from 'react-plotly.js';

const ChartDisplay = ({ charts, resultMessage, chartConfig = {} }) => {
  const parseChartData = (chart) => {
    try {
      const parsedChart = JSON.parse(chart);

      if (parsedChart.data) {
        const updatedData = parsedChart.data.map((item) => {
          // Handle 'indicator' type (displaying as a bar chart)
          if (item.type === 'indicator') {
            return {
              ...item,
              type: 'bar',
              x: ['Indicator'],
              y: [item.value],
            };
          }

          // Handle 'pie' type (rendering a pie chart)
          if (item.type === 'pie') {
            return {
              ...item,
              type: 'pie',
              values: item.values,
              labels: item.labels,
              hoverinfo: 'label+percent',
            };
          }

          // Handle 'scatter' type (rendering a scatter plot)
          if (item.type === 'scatter') {
            return {
              ...item,
              type: 'scatter',
              mode: item.mode || 'markers', // Default mode: markers
              hoverinfo: item.hoverinfo || 'text+name',
            };
          }

          // Handle 'histogram2d' type (rendering a 2D histogram)
          if (item.type === 'histogram2d') {
            return {
              ...item,
              type: 'histogram2d',
              colorscale: item.colorscale || 'Viridis', // Default colorscale
              colorbar: { title: 'Count' },
            };
          }

          // Default case for unknown plot types (fallback to bar chart)
          return item;
        });

        return {
          data: updatedData,
          layout: {
            title: parsedChart.layout?.title || 'Chart', // Ensure title is added
            xaxis: parsedChart.layout?.xaxis || { title: 'X Axis' },
            yaxis: parsedChart.layout?.yaxis || { title: 'Y Axis' },
            ...chartConfig.layout,
          },
        };
      }

      // Fallback if no data is found
      return {
        data: [{ type: 'bar', x: ['No data'], y: [0] }],
        layout: { title: 'No Data Available' },
      };
    } catch (error) {
      console.error('Error parsing chart data:', error);
      return {
        data: [{ type: 'bar', x: ['Error'], y: [0] }],
        layout: { title: 'Error loading chart' },
      };
    }
  };

  const chartEntries = charts ? Object.values(charts) : [];

  return (
    <div>
      {resultMessage && (
        <p className="text-green-600 text-lg font-semibold">{resultMessage}</p>
      )}

      <div>
        {chartEntries.length > 0 ? (
          chartEntries.map((chart, index) => {
            const parsedData = parseChartData(chart);
            return (
              parsedData && (
                <div key={index} className="bg-gray-100 p-4 rounded-md shadow-md">
                  {/* Render Plotly graph with title */}
                  <Plot
                    data={parsedData.data}
                    layout={parsedData.layout}
                    config={{
                      responsive: true,
                      displayModeBar: true,
                      modeBarButtonsToRemove: ['zoom2d', 'pan2d'],
                      ...chartConfig.plotConfig,
                    }}
                  />
                  {/* Display title if it's available */}
                    <h3 className="text-xl font-semibold text-center mt-2">
                        {parsedData.data[0]?.x[0]?.text || 'Unknown Title'} {/* Safely extract text from object */}
                    </h3>
                </div>
              )
            );
          })
        ) : (
          <p className="text-gray-500">No charts to display</p>
        )}
      </div>
    </div>
  );
};

export default ChartDisplay;
