const express = require("express");
const app = express();
const morgan = require("morgan");
const parser = require("body-parser");
const port = process.env.PORT || 4001;
require("dotenv").config();

app.use(morgan("dev"));
app.use(parser.json());
app.use(parser.urlencoded({ extended: true }));

app.use("/api", require("./api/pyroute"));

app.listen(port, () => console.log("listening on port " + port));
