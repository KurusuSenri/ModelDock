// 登出功能
async function logout() {
    try {
  // 调用后端登出接口
  await fetch("/api/logout/", {
    method: "POST",
    credentials: "include", // 确保发送 Cookie
  });

  // 删除前端存储的 token
  document.cookie =
    "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    `user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`

  // 跳转回登录页
  window.location.href = "/login.html";
} catch (error) {
  console.error("Logout failed:", error);
}
}

logout()
