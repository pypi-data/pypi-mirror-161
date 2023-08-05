/**
 * @file implicit SDK Auto generated JS module.
 * @see https://github.com/meena-erian/implicit-sdk
 * @author Menas (Meena) Erian
 * @copyright (C) 2022 Menas (Meena) Erian
 */


 function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

function getCsrfToken(){
  return getCookie('csrftoken');
}

 var call = {
  timeout: -1,
  stack: [],
  send: function () {
    if (call.stack.length) {
      let s = call.stack;
      call.stack = [];
      fetch("pathToEndpoint", {
        "headers": {
          "Content-Type": "application/json;charset=UTF-8",
          "X-CSRFToken": getCsrfToken()
        },
        "method": "POST",
        "credentials": "include",
        "body": JSON.stringify(s)
      }).then(
        async r => call.resolve(s, r),
        async r => call.reject(s, r)
      )
    }
  },
  resolve: async function (callStack, serverResponse) {
    serverResponse = await serverResponse.json()
    serverResponse.forEach((element, i) => {
      if("returned" in element){
        callStack[i].promise.resolve(element.returned);
      }
      else{
        callStack[i].promise.reject(element.exception)
      }
    });
  },
  reject: function (callStack) {
    callStack.forEach((c) => {
      c.promise.reject("Connection failed");
    });
  },
};


