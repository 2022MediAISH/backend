// 배포 이후에 중요한 키 값 넣어둘 곳
module.exports = {
  mongoURI: process.env.MONGOURI //MONGOURI는 배포할 곳 ex. heroku에서 환경변수로 따로 저장해둔 것
};