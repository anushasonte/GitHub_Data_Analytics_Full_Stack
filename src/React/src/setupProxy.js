const { createProxyMiddleware } = require("http-proxy-middleware");

/*
This acts a proxy between the react application and the flask microservice
Everytime there is a request to /api, the setupProxy prepends the flask
microservice url mentioned in line 14
*/
module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      // update the flask Google Cloud url

     target: "https://flask-4gjembatva-uc.a.run.app",
      //target: "http://localhost:5001",
      changeOrigin: true,
    })
  );
};