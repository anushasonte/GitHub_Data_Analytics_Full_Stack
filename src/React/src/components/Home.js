/*
Goal of React:
  1. React will retrieve GitHub created and closed issues for a given repository and will display the bar-charts 
     of same using high-charts        
  2. It will also display the images of the forecasted data for the given GitHub repository and images are being retrieved from 
     Google Cloud storage
  3. React will make a fetch api call to flask microservice.
*/

// Import required libraries
import * as React from "react";
import { useState } from "react";
import Box from "@mui/material/Box";
import Drawer from "@mui/material/Drawer";
import AppBar from "@mui/material/AppBar";
import CssBaseline from "@mui/material/CssBaseline";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
// Import custom components
import BarCharts from "./BarCharts";
import LineCharts from "./LineCharts";
import AllReposBarCharts from "./AllReposBarCharts";
import StackedBarCharts from "./StackedBarCharts";
import Loader from "./Loader";
import { ListItemButton } from "@mui/material";

const drawerWidth = 240;
// List of GitHub repositories 
const repositories = [
  {
    key: "common-graphs",
    value: "Common Graphs",
  },
  {
    key: "angular/angular",
    value: "Angular",
  },
  {
    key: "angular/angular-cli",
    value: "Angular-cli",
  },
  {
    key: "d3/d3",
    value: "D3",
  },
  {
    key: "golang/go",
    value: "GoLang",
  },
  {
    key: "openai/openai-cookbook",
    value: "OpenAI Codebook",
  },
  {
    key: "openai/openai-python",
    value: "OpenAI Python",
  },
  {
    key: "milvus-io/pymilvus",
    value: "Milvus",
  },
  {
    key: "SeleniumHQ/selenium",
    value: "Selenium",
  },
  {
    key: "google/go-github",
    value: "Google",
  },
  {
    key: "facebook/react",
    value: "React",
  },
  {
    key: "tensorflow/tensorflow",
    value: "Tensorflow",
  },
  {
    key: "keras-team/keras",
    value: "Keras",
  },
];

export default function Home() {
  /*
  The useState is a react hook which is special function that takes the initial 
  state as an argument and returns an array of two entries. 
  */
  /*
  setLoading is a function that sets loading to true when we trigger flask microservice
  If loading is true, we render a loader else render the Bar charts
  */
  const [loading, setLoading] = useState(true);
  const [graphData, setGraphData] = useState(true);
  /* 
  setRepository is a function that will update the user's selected repository such as Angular,
  Angular-cli, Material Design, and D3
  The repository "key" will be sent to flask microservice in a request body
  */
  const [repository, setRepository] = useState({
    key: "angular/angular",
    value: "Angular",
  });
  /*
  
  The first element is the initial state (i.e. githubRepoData) and the second one is a function 
  (i.e. setGithubData) which is used for updating the state.

  so, setGitHub data is a function that takes the response from the flask microservice 
  and updates the value of gitHubrepo data.
  */
  const [githubRepoData, setGithubData] = useState([]);
  const [allReposData, setAllReposData] = useState([]);


  const eventHandler = (repo) => {
    if (repo.key === "common-graphs") {
      showCommonGraphs();
    } 
    else {
      setRepository(repo);
      setGraphData(true);
    }
  };

  const showCommonGraphs = () => {
    setLoading(false);
    setRepository("");
    setGithubData([]);
    setGraphData(false);
    // You can add additional logic or components related to "Common Graphs" here
  };

  const repositoriesObject = {};

  for (const repo of repositories) {
    if (repo.key !== "common-graphs") {
      repositoriesObject[String(repo.value)] = String(repo.key);
    }
  }
  /* 
  Fetch the data from flask microservice on Component load and on update of new repository.
  Everytime there is a change in a repository, useEffect will get triggered, useEffect inturn will trigger 
  the flask microservice 
  */
  React.useEffect(() => {
    // set loading to true to display loader
    setLoading(true);
    const requestOptions = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // Append the repository key to request body
      body: JSON.stringify({ repository: repository.key }),
    };
    const requestOptionsForAllData = {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // Append the repository key to request body
      body: JSON.stringify({ repositories: repositoriesObject}),

    };

    console.log(JSON.stringify({ repositories: repositoriesObject}));



    /*
    Fetching the GitHub details from flask microservice
    The route "/api/github" is served by Flask/App.py in the line 53
    @app.route('/api/github', methods=['POST'])
    Which is routed by setupProxy.js to the
    microservice target: "your_flask_gcloud_url"
    */
    fetch("/api/github", requestOptions)
      .then((res) => res.json())
      .then(
        // On successful response from flask microservice
        (result) => {
          // On success set loading to false to display the contents of the resonse
          setLoading(false);
          // Set state on successfull response from the API
          setGithubData(result);
        },
        // On failure from flask microservice
        (error) => {
          // Set state on failure response from the API
          console.log(error);
          setLoading(false);
          setGithubData([]);
        }
      );
    // Fetch data from /api/github/allreposdata
  fetch("/api/github/allreposdata",requestOptionsForAllData)
  .then((res) => res.json())
  .then(
    // On successful response from the second endpoint
    (allRepoResult) => {
      // Set state to store the data from the second endpoint
      console.log(allRepoResult);
      setAllReposData(allRepoResult);
      setGraphData(true);
    },
    // On failure from the second endpoint
    (error) => {
      console.log(error);
      setAllReposData([]);
      setGraphData(false);
      // Handle the error as needed
    }
  );
  }, [repository]);

  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      {/* Application Header */}
      <AppBar
        position="fixed"
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Timeseries Forecasting
          </Typography>
        </Toolbar>
      </AppBar>
      {/* Left drawer of the application */}
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: drawerWidth,
            boxSizing: "border-box",
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: "auto" }}>
          <List>
            {/* Iterate through the repositories list */}
            {repositories.map((repo) => (
              <ListItem
                button
                key={repo.key}
                onClick={() => eventHandler(repo)}
                disabled={loading && repo.value !== repository.value}
              >
                <ListItemButton selected={repo.value === repository.value}>
                  <ListItemText primary={repo.value} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {/* Render loader component if loading is true else render charts and images */}
        {loading ?  (
          <Loader />
        ) : (
          graphData && (
          <div>
            {/* Render barchart component for a monthly created issues for a selected repositories*/}
            <BarCharts
              title={`Created Issues for ${repository.value} in last 2 months`}
              data={githubRepoData?.created}
            />
            {/* Render barchart component for a monthly created issues for a selected repositories*/}
            <BarCharts
              title={`Closed Issues for ${repository.value} in last 8 weeks`}
              data={githubRepoData?.weeklyClosed}
            />
            <Divider
              sx={{ borderBlockWidth: "3px", borderBlockColor: "#FFA500" }}
            />
            {/* Rendering Timeseries Forecasting of Created Issues using Tensorflow and
                Keras LSTM */}
            <div>
              <Typography variant="h5" component="div" gutterBottom style={{textAlign: 'center',textDecoration: 'underline', }}> 
                Timeseries Forecasting using Tensorflow and Keras LSTM 
              </Typography>
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues created for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.lstmData?.dayOfWeekMaxCreated} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.lstmData?.dayOfWeekMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The month of the year maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.lstmData?.monthOfYearMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Created Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Created Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Closed Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Closed Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Pulls Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Pulls Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Commits Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Commits Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Branches Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Branches Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Contributers Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Contributers Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Releases Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.all_issues_data_image
                  }
                  alt={"Releases Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                  Model Loss for Created Issues
                </Typography>
                {/* Render the model loss image for created issues */}
                <img
                  src={githubRepoData?.createdAtImageUrls?.model_loss_image_url}
                  alt={"Model Loss for Created Issues"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                  LSTM Generated Data for Created Issues
                </Typography>
                {/* Render the LSTM generated image for created issues*/}
                <img
                  src={
                    githubRepoData?.createdAtImageUrls?.lstm_generated_image_url
                  }
                  alt={"LSTM Generated Data for Created Issues"}
                  loading={"lazy"}
                />
              </div>
              
            </div>
            <Divider
              sx={{ borderBlockWidth: "3px", borderBlockColor: "#FFA500" }}
            />
            <div>
              <Typography variant="h5" component="div" gutterBottom style={{textAlign: 'center',textDecoration: 'underline', }}> 
                Timeseries Forecasting using Prophet
              </Typography>
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues created for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.prophetForecastData?.dayOfWeekMaxCreated} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.prophetForecastData?.dayOfWeekMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The month of the year maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.prophetForecastData?.monthOfYearMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Created Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.createdIssuesForecast
                  }
                  alt={"Created Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Closed Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.closedIssuesForecast
                  }
                  alt={"Closed Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Pulls Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.pullsForecast
                  }
                  alt={"Pulls Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Commits Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.commitsForecast
                  }
                  alt={"Commits Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Branches Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.branchesForecast
                  }
                  alt={"Branches Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Contributers Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.contributersForecast
                  }
                  alt={"Contributers Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Releases Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.prophetForecastData?.releasesForecast
                  }
                  alt={"Releases Forecast"}
                  loading={"lazy"}
                />
              </div>
              
            </div>
            <Divider
              sx={{ borderBlockWidth: "3px", borderBlockColor: "#FFA500" }}
            />
            <div>
              <Typography variant="h5" component="div" gutterBottom style={{textAlign: 'center',textDecoration: 'underline', }}> 
                Timeseries Forecasting using StatsModel 
              </Typography>
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues created for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.statsModelForecastData?.dayOfWeekMaxCreated} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The day of the week maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.statsModelForecastData?.dayOfWeekMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                The month of the year maximum number of issues closed for {repository.value} is : 
                <br/>
                <div style={{ textAlign: 'center' }}>
                <strong> {githubRepoData?.statsModelForecastData?.monthOfYearMaxClosed} </strong>
                </div>
                </Typography>
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Created Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.createdIssuesForecast
                  }
                  alt={"Created Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Closed Issues Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.closedIssuesForecast
                  }
                  alt={"Closed Issues Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Pulls Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.pullsForecast
                  }
                  alt={"Pulls Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Commits Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.commitsForecast
                  }
                  alt={"Commits Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Branches Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.branchesForecast
                  }
                  alt={"Branches Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Contributers Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.contributersForecast
                  }
                  alt={"Contributers Forecast"}
                  loading={"lazy"}
                />
              </div>
              <Divider
              sx={{ borderBlockWidth: "1px", borderBlockColor: "#FFA500" }}
              />
              <div>
                <Typography component="h4">
                Releases Forecast
                </Typography>
                {/* Render the all issues data image for created issues*/}
                <img
                  src={
                    githubRepoData?.statsModelForecastData?.releasesForecast
                  }
                  alt={"Releases Forecast"}
                  loading={"lazy"}
                />
              </div>
              
            </div>
            
          </div>
        ))}
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
  <Toolbar />
  {/* Render loader component if loading is true else render charts and images */}
  {loading ? (
    <Loader />
  ) : (
    !graphData && (
      <div>
      {/* Render a Line Chart to plot the issues for every Repo*/}
      <LineCharts
        title={`A Line Chart to plot the issues for every Repo`}
        data={allReposData?.items}
      /> 
    
      {/*
      <BarCharts
        title={`A Bar Chart to plot the issues created every month for every Repo`}
        data={allReposData?.items}
      />  */}
      {/* A Bar Chart to plot the stars for every Repo*/}
      <AllReposBarCharts
        title={`A Bar Chart to plot the stars for every Repo`}
        data={allReposData?.items}
        displayStarCount={true}
      />
      {/* A Bar Chart to plot the forks for every Repo*/}
      <AllReposBarCharts
        title={`A Bar Chart to plot the forks for every Repo`}
        data={allReposData?.items}
        displayStarCount={false}
      />
      {/*
      <BarCharts
        title={`A Bar Chart to plot the issues closed every week for every Repo`}
        data={allReposData?.repoName}
  /> */}
      <StackedBarCharts
        title={`A Stack-Bar Chart to plot the created and closed issues for every Repo`}
        data={allReposData?.items}
      /> 
      </div>
    )
  )}
</Box>
    </Box>
    
  );
}
