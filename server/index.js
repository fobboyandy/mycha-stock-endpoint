const express = require("express");
const app = express();
const morgan = require("morgan");
const parser = require("body-parser");
const port = process.env.PORT || 4001;

app.use(morgan("dev"));
app.use(parser.json());
app.use(parser.urlencoded({ extended: true }));

// /assets virtual path for the images
app.use("/api", require("./api/pyroute"));

app.listen(port, () => console.log("listening on port " + port));

// use vite's connect instance as middleware
// if you use your own express router (express.Router()), you should use router.use
