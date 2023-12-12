import React from "react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

const AllReposBarCharts = (props) => {
  const { title, data, displayStarCount } = props;

  const yAxisTitle = displayStarCount ? "Star Count" : "Fork Count";

  const config = {
    chart: {
      type: "column",
    },
    title: {
      text: title,
    },
    xAxis: {
      type: "category",
      labels: {
        rotation: -45,
        style: {
          fontSize: "13px",
          fontFamily: "Verdana, sans-serif",
        },
      },
    },
    yAxis: {
      min: 0,
      title: {
        text: yAxisTitle,
      },
    },
    legend: {
      enabled: false,
    },
    tooltip: {
      pointFormat: `${yAxisTitle}: <b>{point.y} </b>`,
    },
    series: [
      {
        name: title,
        data: data.map((repo) => ({
          name: repo.reponame,
          y: displayStarCount ? repo.starCount : repo.forkCount,
        })),
        dataLabels: {
          enabled: true,
          rotation: -90,
          color: "#FFFFFF",
          align: "right",
          format: "{point.y}", // one decimal
          y: 10, // 10 pixels down from the top
          style: {
            fontSize: "13px",
            fontFamily: "Verdana, sans-serif",
          },
        },
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

export default AllReposBarCharts;
