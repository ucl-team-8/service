import d3 from "d3";

export default function get(type, url) {
  return new Promise(function(resolve, reject) {
    d3[type](url, function(error, data) {
      if (error) return reject(error);
      else return resolve(data);
    })
  });
}
