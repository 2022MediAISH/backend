const express = require("express"); // express module을 가져온다
const app = express(); // 모듈을 이용해 새 앱을 만든다.
const port = 5000;
const config = require("./config/key");
const qs = require("query-string");
const bodyParser = require("body-parser");
const cors = require('cors')
// const { Ddata } = require("./models/Ddata");

// application/x-www-form-urlencoded 형식으로 된 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.urlencoded({ extended: true })); //클에서오는 정보를 서버에서 분석해서 가져올 수 있게 해줌
// applicaiton/json 형식의 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.json());

app.use(cors())

const spawn = require("child_process").spawn;

app.get("/create/:NCTNO", (req, res) => {});
// const mongoose = require("mongoose");
// const database =
// mongoose
//   .connect(config.mongoURI, {})
//   .then(() => console.log("MongoDB connected SUCCESS"))
//   .catch((err) => console.log(err));

// const MongoClient = require("mongodb").MongoClient;
// MongoClient.connect(
//   config.mongoURI,
//   { useUnifiedTopology: true },
//   function (err, db) {
//     if (err) throw err;
//     var dbo = db.db("testdb");
//     var query = { _id: "NCT01967771" }; // 이거 바꿔야함

//     dbo.collection("test01").findOne(query, function (err, result) {
//       if (result) {
//         resolve(result);
//       }
//     });
//   }
// )
//   .then(() => console.log("MongoDB connected SUCCESS"))
//   .catch((err) => console.log(err));

// req: 요청, res: 응답
app.post("/api", (req, res) => {
  // console.log(req);
  const post = req.body;
  console.log(post);
  input = post.url; //url은 key의 이름임

  const Url = input;
  // const Url = "https://www.clinicaltrials.gov/ct2/show/NCT04577378";
  console.log("#####", Url);
  const python_result = spawn("/home/jun/anaconda3/bin/python", [
    "./resource_control.py",
    Url,
  ]);

  let getJson;
  let result_json;
  python_result.stdout.on("data", (data) => {
    console.log(`stdout: ${data.toString()}`);
    getJson = data.toString();
    getJson = getJson.replaceAll('\'', '\"');
  
    result_json = JSON.parse(getJson);
  });

  python_result.stderr.on("data", (data) => {
    console.error(`stderr: ${data.toString()}`);
  });

  python_result.on("close", (code) => {
    console.log(`child process exited with code ${code}`);
    // console.log('======', typeof result_json); // string
    res.json(result_json);
  
    ///// 데이터 받은거 저장
    // ddata.save((err, doc)=>{
    //   if(err) return res.json({success: false, err});
    //   return res.status(200).json({
    //     success: true
    //   });
    // })
    // res.send(ddata);
    // return res.json(python_result);
    // res.redirect('/')
  });

});

app.get("/api/hello", (req, res) => {
  console.log(req.body);
  res.send("hi");
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
