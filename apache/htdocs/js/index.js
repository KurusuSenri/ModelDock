const username = getCookie("user_id");
const welcomeElement = document.getElementById("welcome-message");
welcomeElement.innerHTML = `Welcome, <strong>${username}</strong>`;
