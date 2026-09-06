const apiUrl = apiServer + "api/tasks/";

// 渲染表格
function renderTable(data) {
  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML = ""; // 清空现有内容

  data.result.forEach((task) => {
    const row = document.createElement("tr");
    row.innerHTML = `
                    <td><a href="get_task.html?task_id=${task.task_id}">${task.task_id}</a></td>
                    <td>${task.task_desc}</td>
                    <td>${task.status}</td>
                    <td><a href="get_model.html?model_id=${task.model_id}">${task.model_id}</a></td>
                    <td>${task.error_message}</td>
                    <td>${task.start_date}</td>
                    <td>${task.end_date}</td>
                `;
    console.log(row.innerHTML)
    tableBody.appendChild(row);
  });
}

// 页面加载时获取数据
document.addEventListener("DOMContentLoaded", () => {
  const errorElement = document.getElementById("error");
  fetchDataFromAPI()
    .then((data) => {
        console.log(data.result);
      renderTable(data);
    })
    .catch((error) => {
      errorElement.style.display = "block";
      errorElement.textContent = `加载失败: ${error.log_id} ${error.error}`;
    });
});