import d3 from "d3";

/*

A wrapper that makes d3 request methods to return promises instead of taking
callbacks as parameters.

E.g.

    get("json", "/data.json").then((data) => { ...something... });

is equivalent to:

    d3.json("./data.json", (data) => { ...something... })

*/

export default function get(type, url) {
  return new Promise(function(resolve, reject) {
    d3[type](url, function(error, data) {
      if (error) return reject(error);
      else return resolve(data);
    })
  });
}
