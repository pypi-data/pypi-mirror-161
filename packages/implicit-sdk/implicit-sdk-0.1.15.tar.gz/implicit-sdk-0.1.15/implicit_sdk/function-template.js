
async function functionName(argList) {
  let params = Array.prototype.slice.call(arguments);
  var p = new Promise(function (resolve, reject) {
    call.stack.push({
      name: "functionName",
      params: params,
      promise: {
        resolve: resolve,
        reject: reject,
      },
    });
  });
  if (call.timeout !== -1) clearTimeout(call.timeout);
  call.timeout = setTimeout(call.send, 700);
  return p;
}
