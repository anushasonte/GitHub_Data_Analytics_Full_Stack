import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const LineChart = (props) => {
  const { title, data } = props;

  if (!data || data.length === 0) {
    // Handle the case when data is not available
    return <div>No data available for the chart.</div>;
  }

  const config = {
    chart: {
      type: "line",
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
    },
    series: [
      {
        name: "Total Issues",
        data: data.map((repo) => repo.issuesClosed + repo.issuesCreated),
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

export default LineChart;
