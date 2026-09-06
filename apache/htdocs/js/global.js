function getCookie(name) {
  const cookies = document.cookie.split(";");
  for (let cookie of cookies) {
    const [cookieName, cookieValue] = cookie.trim().split("=");
    if (cookieName === name) {
      return decodeURIComponent(cookieValue);
    }
  }
  return null;
}

// 格式化 JSON
function formatJson(data) {
  return JSON.stringify(data, null, 2)
    .replace(/\n/g, "<br>")
    .replace(/ /g, "&nbsp;");
}

function fetchDataFromAPI() {
  return new Promise((resolve, reject) => {
    fetch(apiUrl, {
      headers: {
        "Content-Type": "application/json",
        Authorization: getCookie("access_token"),
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.log_id != 200) {
          reject({
            log_id: data.log_id,
            error: data.error,
          });
        } else {
          resolve(data);
        }
      })
      .catch((error) => reject(error));
  });
}


// 如果没有 token 则跳转到登录页
const accessToken = getCookie("access_token");
if (!accessToken) {
  window.location.href = "/login.html";
}

const apiServer = 'http://localhost:5000/'

const pageHeaderElement = document.getElementById("pageHeader");
fetch("/header.html")
  .then((response) => response.text())
  .then((html) => {
    pageHeaderElement.innerHTML = html;
  });