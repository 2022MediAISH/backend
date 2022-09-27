const express = require("express"); // express module을 가져온다
const app = express(); // 모듈을 이용해 새 앱을 만든다.
const port = 5000;
const config = require("./config/key");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const cors = require("cors");
const https = require("https");
const { resourceLimits } = require("worker_threads");
// const { Ddata } = require("./models/Ddata");

const DATABASE_NAME = "testdb";
let database, collection;

// application/x-www-form-urlencoded 형식으로 된 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.urlencoded({ extended: true })); //클라이언트에서 오는 정보를 서버에서 분석해서 가져올 수 있게 해줌
// applicaiton/json 형식의 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.json());

app.use(cors());
app.use(express.json());

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

app.get("/api/:NCTNO", async (req, res) => {
  const { NCTNO } = req.params;
  console.log(NCTNO);
  let query = { _id: NCTNO };
  let result_json;
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
        const python_result = spawn("python3", [
          "./resource_control.py",
          NCTNO,
        ]);

        let getJson;
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
        });
      }
      console.log("finish!====");
    }
  });
});

app.post("/api", (req, res) => {
  console.log(req.body);
  res.send(req.body);
})

// app.post("/api", async (req, res) => {
//   // console.log(req);
//   const post = req.body;
//   console.log(post);
//   input = post.url; //url은 key의 이름임

//   let Url = input;
//   console.log("#####", Url); // url
//   let NCTID;

//   //NCT 번호를 뽑아내기 위한 작업
//   if (Url.includes("NCT") === true) {
//     //이미 URL이 NCT를 가지고 있는 경우
//     let Htmltext = Url;
//     let findtext = Htmltext.match("NCT[0-9]+"); //NCT를 찾아 번호를 뽑아낸다.
//     NCTID = findtext[0];
//   } else {
//     // NCT를 가지고 있지 않은 경우
//     // { "url": "https://www.clinicaltrials.gov/api/query/full_studies?expr=Effect%20of%20Carbamazepine%20on%20Dolutegravir%20Pharmacokinetics" }

//     // URL이 이미 json 형태인 경우
//     if (Url.includes("json") !== true) {
//       // URL이 json이 아닌 경우
//       let expr = Url.match("expr=[0-9a-zA-Z%+.]+")[0];
//       // console.log("expr", expr);
//       Url =
//         "https://clinicaltrials.gov/api/query/full_studies?" +
//         expr +
//         "&fmt=json";
//       console.log(Url);
//     }

//     https.get(Url, (res) => {
//       let rawHtml = "";
//       res.on("data", (chunk) => {
//         rawHtml += chunk;
//       });
//       res.on("end", () => {
//         try {
//           Htmltext = JSON.parse(rawHtml);
//           NCTID =
//             Htmltext.FullStudiesResponse.FullStudies[0].Study.ProtocolSection
//               .IdentificationModule.NCTId;
//         } catch (e) {
//           console.error(e.message);
//         }
//       });
//     });
//   }
//   // NCTID 추출하기전에 미리 117번 줄이 실행됨. 그래서 NCTID가 undefined기에 바로 resourceControl 실행되는 것.
//   //MongoDB에서 가져옴
//   let query = { _id: NCTID };
//   let result_json;
//   // console.log("mongo 진입 전");
//   await collection.findOne(query, (error, result) => {
//     if (error) {
//       console.log("findOne's error not empty result: ", error);
//     } else {
//       console.log("hello");
//       if (result !== null) {
//         console.log("MongoDB\n");
//         console.log(result);
//         res.json(result);
//       } else {
//         // resource_control 실시간으로 돌리기
//         const python_result = spawn("python3", [
//           "./resource_control.py",
//           Url,
//         ]);

//         let getJson;
//         python_result.stdout.on("data", (data) => {
//           console.log(`stdout: ${data.toString()}`);
//           getJson = data.toString();
//           getJson = getJson.replaceAll("'", '"');

//           result_json = JSON.parse(getJson);
//           res.json(result_json);
//         });
//         python_result.stderr.on("data", (data) => {
//           console.error(`stderr: ${data.toString()}`);
//         });

//         python_result.on("close", (code) => {
//           console.log(`child process exited with code ${code}`);
//         });
//       }
//       console.log("finish!====");
//     }
//   });
// });

app.post("/crawling", async (req, res) => {
  const post = req.body;
  console.log(post);
  input = post.url;
  let NCTID = input;
  //crawlling
  const originalText = spawn("python", [
    "./crawling.py",
    NCTID,
  ]);
  let getResult;
  originalText.stdout.on("data", (data) => {
    // console.log(`stdout: ${data.toString()}`); // this works well
    getResult = data.toString();
    // console.log("data: ", getResult);
    res.send(getResult);
  });
  originalText.stderr.on("data", (data) => {
    console.error(`stderr: ${data.toString()}`);
  });

  originalText.on("close", (code) => {
    console.log(`crawling _ child process exited with code ${code}`);
  });
});
