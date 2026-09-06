const apiUrl = apiServer + "api/models/";

// 渲染表格
function renderTable(data) {
  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML = ""; // 清空现有内容

  console.log(data.result)
  data.result.forEach((model) => {
    const row = document.createElement("tr");
    row.innerHTML = `
                    <td><a href="get_model.html?model_id=${model.model_id}">${model.model_id}</a></td>
                    <td>${model.model_type}</td>
                    <td>${model.model_desc}</td>
                    <td>${model.model_date}</td>
                    <td class="json-cell">${formatJson(JSON.parse(model.model_column))}</td>
                    <td class="json-cell">${formatJson(model.model_label)}</td>
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
      renderTable(data);
    })
    .catch((error) => {
      errorElement.style.display = "block";
      errorElement.textContent = `加载失败: ${error.log_id} ${error.error}`;
    });
});