const express = require("express");
const app = express();
const morgan = require("morgan");
const parser = require("body-parser");
const path = require("path");
const port = process.env.PORT || 4001;
const { createServer } = require("vite");

app.use(morgan("dev"));
app.use(parser.json());
app.use(parser.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "../dist")));

// /assets virtual path for the images
app.use("/assets", express.static(path.join(__dirname, "../assets")));
app.use("/api", require("./api/pyroute"));

// app.post("/api/123", (req, res) => {
//   const data = req.body;
//   let dataToSend;
//   let largeDataSet = [];
//   // spawn new child process to call the python script
//   const python = spawn("python3", ["script1.py"]);

//   // collect data from script
//   python.stdout.on("data", function (data) {
//     console.log("Pipe data from python script ...");
//     //dataToSend =  data;
//     largeDataSet.push(data);
//   });

//   console.log(largeDataSet);

//   // in close event we are sure that stream is from child process is closed
//   python.on("close", (code) => {
//     console.log(`child process close all stdio with code ${code}`);
//     // send data to browser
//     res.send(largeDataSet.join(""));
//   });
// });

const v = async function () {
  const vite = await createServer({
    server: { middlewareMode: true },
    appType: "custom",
  });

  app.use(vite.middlewares);
};

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "../dist/index.html"));
});

app.listen(port, () => console.log("listening on port " + port));
v();

// use vite's connect instance as middleware
// if you use your own express router (express.Router()), you should use router.use
