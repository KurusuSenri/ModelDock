const urlParams = new URLSearchParams(window.location.search);
const model_id = urlParams.get("model_id");
const apiUrl = apiServer + "api/models/" + model_id + "/";
// 渲染表格
function renderTable(data) {
  model = data.result;
  document.getElementById("model_id").innerHTML = model.model_id;
  document.getElementById("model_type").innerHTML = model.model_type;
  document.getElementById("model_desc").innerHTML = model.model_desc;
  document.getElementById("model_date").innerHTML = model.model_date;
  document.getElementById("model_column").innerHTML = formatJson(
    JSON.parse(model.model_column)
  );
  document.getElementById("model_label").innerHTML = formatJson(
    model.model_label
  );

  const tasksTableBody = document.getElementById("tasksTableBody");
  tasksTableBody.innerHTML = ""; // 清空现有内容

  data.result.tasks.forEach((task) => {
    const row = document.createElement("tr");

    row.innerHTML = `
                    <td><a href="/get_task.html?task_id=${task.task_id}">${task.task_id}</a></td>
                    <td>${task.task_desc}</td>
                    <td>${task.status}</td>
                    <td>${task.start_date}</td>
                    <td>${task.end_date}</td>
                `;
    console.log(row.innerHTML);
    tasksTableBody.appendChild(row);
  });
}

// 页面加载时获取数据
document.addEventListener("DOMContentLoaded", () => {
  const errorElement = document.getElementById("error");
  const deleteLink = document.getElementById("delete_model");
  deleteLink.href = `/delete_model.html?model_id=${model_id}`
  const createLink = document.getElementById("create_task");
  createLink.href = `/create_task.html?model_id=${model_id}`

  fetchDataFromAPI()
    .then((data) => {
      renderTable(data);
    })
    .catch((error) => {
      errorElement.style.display = "block";
      errorElement.textContent = `加载失败: ${error.log_id} ${error.error}`;
    });
});

