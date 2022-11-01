const express = require("express"); // express module을 가져온다
const app = express(); // 모듈을 이용해 새 앱을 만든다.
const port = 5000;
const config = require("./config/key");
const bodyParser = require("body-parser");
const MongoClient = require("mongodb").MongoClient;
const cors = require("cors");
const https = require("https");
const fs = require('fs');
const { Console } = require('console');
const path = require("path");


const DATABASE_NAME = "testdb";
let database, collection;

let isProd = true;
let pythonPath = '/home/ubuntu/22SH/2ndIntegration/backendNodeJS/venPy8/bin/python';
if (isProd == false) {
  pythonPath = '/home/jun/anaconda3/bin/python';
}

// application/x-www-form-urlencoded 형식으로 된 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.urlencoded({ extended: true })); //클라이언트에서 오는 정보를 서버에서 분석해서 가져올 수 있게 해줌
// applicaiton/json 형식의 데이터를 분석해서 가져올 수 있게 해줌
app.use(bodyParser.json());

app.use(cors());
app.use(express.static(path.join(__dirname, '../frontendReact/build')));
app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, '../frontendReact/build/index.html'))
})

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
      collection = database.collection("test02");
      console.log("Connected to `" + DATABASE_NAME + "`!");
    }
  );
});

const spawn = require("child_process").spawn;


app.post("/load", (req, res) => { // 편집본이 존재할때 원본 로드
  const NCTID = req.body.url; // body는 NCTID
  console.log(NCTID);
  let query = { _id: NCTID };



  const options = { useUnifiedTopology: true };

  MongoClient.connect(config.mongoURI, options, function (err, db) {

    if (err) throw err;

    const dbo = db.db("testdb");
    const collection_origin = dbo.collection("test02");
    // 본문에서 해당 내용 불러옴
    collection_origin.findOne(query, function (err, result) {
      if (err) throw err;
      else {
        if (result !== null) {
          console.log(result);
          res.json(result);
        }
      }
    });
  });

});



app.post("/api", async (req, res) => {//get요청: 편집본 있으면 편집본, 없으면 원본, 원본도 없으면 리얼타임
  const post = req.body;
  let Url = post.url; //url은 key의 이름임

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
    // { "url": "https://www.clinicaltrials.gov/api/query/full_studies?expr=Effect%20of%20Carbamazepine%20on%20Dolutegravir%20Pharmacokinetics" }

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
  // NCTID 추출하기전에 미리 117번 줄이 실행됨. 그래서 NCTID가 undefined기에 바로 resourceControl 실행되는 것.
  //MongoDB에서 가져옴
  let query = { _id: NCTID };
  let result_json;



  const options = { useUnifiedTopology: true };

  MongoClient.connect(config.mongoURI, options, function (err, db) {

    if (err) throw err;

    const dbo = db.db("testdb");
    const collection = dbo.collection("edit");
    const collection_origin = dbo.collection("test02");

    collection.countDocuments(query, function (err, c) {
      if (err) throw err;
      if (c !== 0) {
        collection.findOne(query, function (err, result) {
          if (err) throw err;
          console.log(`edited${result}`);
          res.json(result);
        })
      }

      // edit collection에 없으면
      else {
        // 본문에서 해당 내용 불러옴
        collection_origin.findOne(query, function (err, result) {
          if (err) throw err;
          else {
            if (result !== null) {
              console.log(`origin${result}`);
              res.json(result);

            }
            else {
              let getJson;
              const result = spawn(pythonPath, ['data_extract_Biolinkbert.py', Url]);
              result.stdout.on('data', function (data) {
                console.log(data.toString());
                getJson = data.toString();
                getJson = getJson.replace(/'/g, '"');
                result_json = JSON.parse(getJson);
                res.json(result_json);
              });
              result.stderr.on('data', function (data) {
                console.log(data.toString());
              });
              result.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
              });
            }
          }
        })
      }
    });
  });
});




app.post("/create", (req, res) => { // req.body는 JSON 값, 편집 저장용 라우터
  console.log(req.body);
  const data = JSON.stringify(req.body);

  fs.writeFileSync(`./NCT_ID_database/${req.body._id}.json`, data, 'utf8', function (error) {
    console.log('writeFile completed');
  });


  const options = { useUnifiedTopology: true };

  MongoClient.connect(config.mongoURI, options, function (err, db) {

    if (err) throw err;

    const dbo = db.db("testdb");
    const collection = dbo.collection("edit");
    const query = { _id: req.body._id };
    var total = 0;

    let data = fs.readFileSync(`./NCT_ID_database/${req.body._id}.json`, 'utf-8');
    let json = JSON.parse(data);

    collection.countDocuments(query, function (err, c) {
      console.log('Count is ' + c);
      if (c == 1) {
        collection.deleteOne(query, function (err, obj) {
          if (err) throw err;
          console.log("delete the same file")
        })
      }
    });

    // 이게 먼저 실행됨 (await 써야할 듯)
    collection.insertOne(json, function (err, res) {
      if (err) throw err;
      console.log("1 document inserted");
      db.close();
    });

  });
  res.send(req.body);
});


// crawlling
app.post("/crawling", async (req, res) => {
  const post = req.body;
  let NCTID = post.url;
  let getResult;
  const result = spawn(pythonPath, ['crawling.py', NCTID]);
  result.stdout.on('data', function (data) {
    // console.log(data.toString());
    getResult = data.toString();
    // console.log("data: ", getResult);
    res.send(getResult);
  });
  result.stderr.on('data', function (data) {
    console.log(data.toString());
  });

  result.on("close", (code) => {
    console.log(`crawling _ child process exited with code ${code}`);
  });

});
