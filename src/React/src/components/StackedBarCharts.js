import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const StackedBarCharts = (props) => {
  const { title, data } = props;

  if (!data || data.length === 0) {
    // Handle the case when data is not available
    return <div>No data available for the chart.</div>;
  }

  const config = {
    chart: {
      type: "bar",
    },
    title: {
      text: title,
    },
    xAxis: {
      categories: data.map((repo) => repo.reponame),
    },
    yAxis: {
      title: {
        text: "Number of Issues",
      },
      stackLabels: {
        enabled: true,
        style: {
          fontWeight: "bold",
          color: "white",
        },
      },
    },
    legend: {
      reversed: true,
    },
    plotOptions: {
      series: {
        stacking: "normal",
      },
    },
    series: [
      {
        name: "Closed Issues",
        data: data.map((repo) => repo.issuesClosed),
      },
      {
        name: "Created Issues",
        data: data.map((repo) => repo.issuesCreated),
      },
    ],
  };

  return (
    <div>
      <div>
        <HighchartsReact highcharts={Highcharts} options={config} />
      </div>
    </div>
  );
};

export default StackedBarCharts;
