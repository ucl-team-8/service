export default function sectionify(array) {
  let accumulator = [];
  for (let i = 0; i < array.length - 1; i++) {
    accumulator.push([array[i], array[i+1]]);
  }
  return accumulator;
}
