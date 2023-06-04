const express = require("express");
const app = express();
const morgan = require("morgan");
const parser = require("body-parser");
const port = process.env.PORT || 4001;
require("dotenv").config();

const { spawn } = require("child_process");

const cron = require("node-cron");

app.use(morgan("dev"));
app.use(parser.json());
app.use(parser.urlencoded({ extended: true }));

app.use("/api", require("./api/pyroute"));

cron.schedule("*/15 * * * *", function () {
  console.log("running every 15 minutes, " + new Date(new Date().getTime()));

  const python = spawn("python3", ["server/api/push_remaining_stock_data.py"]);

  // collect data from script
  python.stdout.on("data", function (data) {
    console.log("Pipe data from python script ...");
    console.log(data?.toString());
  });

  // in close event we are sure that stream is from child process is closed
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);
  });
});

app.listen(port, () => console.log("listening on port " + port));
