const router = require("express").Router();
const { spawn } = require("child_process");

module.exports = router;

router.all("/sendstock/:secretkey", (req, res) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");

  const secret = req.params.secretkey;

  if (secret !== process.env.SECRET_KEY) {
    res.send("acccess denied").status(403);
    return;
  }

  const data = req.body.data;
  const location = req.body.location;

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

  // in close event we are sure that stream is from child process is closed
  python.on("close", (code) => {
    console.log(`child process close all stdio with code ${code}`);

    res.send(result);
  });
});

router.all("/fetchlocations/:secretkey", (req, res, next) => {
  const secret = req.params.secretkey;

  if (secret !== process.env.SECRET_KEY) {
    res.send("access denied").status(403);
    return;
  }

  try {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "X-Requested-With");

    let result = "";
    // spawn new child process to call the python script
    const python = spawn("python3", ["server/api/get_list_of_locations.py"]);

    // collect data from script
    python.stdout.on("data", function (data) {
      result = data;
    });

    // in close event we are sure that stream is from child process is closed
    python.on("close", (code) => {
      console.log(`child process close all stdio with code ${code}`);
      // send data to browser
      // res.send(largeDataSet.join(""));
      res.send(result);
    });
  } catch (error) {
    next(error);
  }
});

router.all("/fetchstock/:location/:secretkey", (req, res) => {
  res.header("Access-Control-Allow-Origin", "*");
  res.header("Access-Control-Allow-Headers", "X-Requested-With");

  const secret = req.params.secretkey;

  if (secret !== process.env.SECRET_KEY) {
    res.send("acccess denied").status(403);
    return;
  }

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
