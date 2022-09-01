const express = require("express"); // express module을 가져온다
const app = express(); // 모듈을 이용해 새 앱을 만든다.
const port = 5000;
const config = require("./config/key");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const cors = require("cors");
const https = require("https");
// const { Ddata } = require("./models/Ddata");

const DATABASE_NAME = "testdb";
let database, collection;

// application/x-www-form-urlencoded 형식으로 된 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.urlencoded({ extended: true })); //클라이언트에서 오는 정보를 서버에서 분석해서 가져올 수 있게 해줌
// applicaiton/json 형식의 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.json());
app.use(cors());

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
  // mongoDB 연결만
  MongoClient.connect(
    config.mongoURI,
    { useNewUrlParser: true },
    (error, client) => {
      if (error) {
        throw error;
      }
      database = client.db(DATABASE_NAME);
      collection = database.collection("test01");
      console.log("Connected to `" + DATABASE_NAME + "`!");
    }
  );
});

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
app.post("/api", async (req, res) => {
  // console.log(req);
  const post = req.body;
  console.log(post);
  input = post.url; //url은 key의 이름임

  let Url = input;
  console.log("#####", Url); // url
  let NCTID;

  //NCT 번호를 뽑아내기 위한 작업
  if (Url.includes("NCT") === true) {
    //이미 URL이 NCT를 가지고 있는 경우
    let Htmltext = Url;
    let findtext = Htmltext.match("NCT[0-9]+"); //NCT를 찾아 번호를 뽑아낸다.
    NCTID = findtext[0];
  } else {
    // NCT를 가지고 있지 않은 경우

    // URL이 이미 json 형태인 경우
    if (Url.includes("json") !== true) {
      // URL이 json이 아닌 경우
      let expr = Url.match("expr=[0-9a-zA-Z%+.]+")[0];
      // console.log("expr", expr);
      Url =
        "https://clinicaltrials.gov/api/query/full_studies?" +
        expr +
        "&fmt=json";
      console.log(Url);
    }

    https.get(Url, (res) => {
      let rawHtml = "";
      res.on("data", (chunk) => {
        rawHtml += chunk;
      });
      res.on("end", () => {
        try {
          Htmltext = JSON.parse(rawHtml);
          NCTID =
            Htmltext.FullStudiesResponse.FullStudies[0].Study.ProtocolSection
              .IdentificationModule.NCTId;
        } catch (e) {
          console.error(e.message);
        }
      });
    });
  }

  //MongoDB에서 가져옴
  let query = { _id: NCTID };
  // console.log("mongo 진입 전");
  await collection.findOne(query, (error, result) => {
    if (error) {
      console.log("findOne's error not empty result: ", error);
    } else {
      
      console.log("hello");
      if (result !== null) {
        console.log("MongoDB\n");
        console.log(result);
        res.json(result);
      } else {
        // resource_control 실시간으로 돌리기
        const python_result = spawn("/home/jun/anaconda3/bin/python", [
          "./resource_control.py",
          Url,
        ]);
    
        let getJson;
        let result_json;
        python_result.stdout.on("data", (data) => {
          console.log(`stdout: ${data.toString()}`);
          getJson = data.toString();
          getJson = getJson.replaceAll("'", '"');
    
          result_json = JSON.parse(getJson);
          res.json(result_json);
        });
        python_result.stderr.on("data", (data) => {
          console.error(`stderr: ${data.toString()}`);
        });
    
        python_result.on("close", (code) => {
          console.log(`child process exited with code ${code}`);
          // console.log('======', typeof result_json); // object
          // res.json(result_json);
    
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
      }
      console.log("finish!====")
    }
  });
  
});

app.get("/api/hello", (req, res) => {
  console.log(req.body);
  res.send("hi");
});
