const router = require("express").Router();
const { spawn } = require("child_process");

module.exports = router;

router.post("/", (req, res) => {
  const data = req.body.data;
  const location = req.body.location;

  console.log(data);
  console.log(location);

  let largeDataSet = [];
  let result = "";
  // spawn new child process to call the python script
  const python = spawn("python3", [
    "server/api/stock_handling.py",
    data,
    location,
  ]);

  // collect data from script
  python.stdout.on("data", function (data) {
    console.log("Pipe data from python script ...");
    //dataToSend =  data;
    // largeDataSet.push(data);
    result = data;
  });

  console.log(largeDataSet);

  // in close event we are sure that stream is from child process is closed
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    // res.send(largeDataSet.join(""));
    res.send(result);
  });
});

router.get("/fetchlocations", (req, res) => {
  let result = "";
  // spawn new child process to call the python script
  const python = spawn("python3", [
    "server/api/get_list_of_locations.py",
    JSON.stringify(req.params.location),
  ]);

  // collect data from script
  python.stdout.on("data", function (data) {
    console.log("Pipe data from python script ...");
    //dataToSend =  data;
    // largeDataSet.push(data);
    result = data;
  });

  // in close event we are sure that stream is from child process is closed
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    // res.send(largeDataSet.join(""));
    res.send(result);
  });
});

router.get("/fetchstock/:location", (req, res) => {
  let largeDataSet = [];
  let result = "";
  // spawn new child process to call the python script
  const python = spawn("python3", [
    "server/api/check_stock.py",
    JSON.stringify(req.params.location),
  ]);

  // collect data from script
  python.stdout.on("data", function (data) {
    console.log("Pipe data from python script ...");
    //dataToSend =  data;
    // largeDataSet.push(data);
    result = data;
  });

  console.log(largeDataSet);

  // in close event we are sure that stream is from child process is closed
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    // res.send(largeDataSet.join(""));
    res.send(result);
  });
});
