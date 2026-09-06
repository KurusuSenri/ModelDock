document
  .getElementById("loginForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault(); // 阻止表单默认提交行为

    const user_id = document.getElementById("user_id").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");
    console.log(user_id);

    try {
      // 发送登录请求到服务器
      const response = await fetch("http://localhost:5000/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: user_id,
          password: password,
        }),
      });

      const data = await response.json();

      if (data.log_id == 200) {
        // 登录成功：保存 token 到 Cookie 并跳转
        document.cookie = `access_token=Bearer ${data.access_token}; path=/; max-age=1800`; // 有效期 30min
        document.cookie = `user_id=${user_id}; path=/; max-age=1800`
        window.location.href = "/index.html"; // 跳转到主页
      }
      else {
        errorMessage.textContent = "Error: " + data.log_id + " " + data.error;
      }
    } catch (error) {
      errorMessage.textContent = "Network error. Please try again.";
      console.error("Login error:", error);
    }
  });
