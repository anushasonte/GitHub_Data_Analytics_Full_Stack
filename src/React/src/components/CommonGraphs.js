import React, { useState, useEffect } from "react";
import BarCharts from "./BarCharts";
import Loader from "./Loader";

const fetchCommonGraphsData = async () => {
    console.log("Inside common-graphs js file");
  // Perform API call to fetch data for "common-graphs"
  try {
    const response = await fetch("/api/github/allreposdata", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        repositories: [
          "Angular: angular/angular",
          "Angular -cli: angular/angular-cli",
          "D3: d3/d3",
          "Angular Material: angular/material",
        ],
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();
    return result.items;
  } catch (error) {
    console.error("Error fetching data for common-graphs:", error);
    return [];
  }
};

const CommonGraphs = ({ setGithubData, setLoading }) => {
  const [commonGraphsData, setCommonGraphsData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const data = await fetchCommonGraphsData();
      setLoading(false);
      setCommonGraphsData(data);
      setGithubData(data); // Set the data for rendering bar charts in Home.js
    };

    fetchData();
  }, [setGithubData, setLoading]);

  return (
    <div>
      hi
      {commonGraphsData.length > 0 ? (
        <>
          {/* Render barchart component for stars */}
          <BarCharts
            title={`Stars for Repositories`}
            data={commonGraphsData.map((repo) => [repo.reponame, repo.starCount])}
          />
          {/* Render barchart component for forks */}
          <BarCharts
            title={`Forks for Repositories`}
            data={commonGraphsData.map((repo) => [repo.reponame, repo.forkCount])}
          />
        </>
      ) : (
        <Loader />
      )}
    </div>
  );
};

export default CommonGraphs;
