const urlParams = new URLSearchParams(window.location.search);
const task_id = urlParams.get("task_id");
const apiUrl = apiServer + "api/tasks/" + task_id + "/";

function createCSVDownloadLink(base64Data, fileName) {
  try {
    // 1. 解码 Base64
    const binaryString = atob(base64Data);

    // 2. 转换为 Blob 对象
    const blob = new Blob([binaryString], { type: "text/csv;charset=utf-8;" });

    // 3. 创建临时下载链接并自动触发点击
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = fileName;
    link.style.display = "none"; // 隐藏元素

    // 4. 添加到页面并自动点击
    document.body.appendChild(link);
    link.click();

    // 5. 清理
    setTimeout(() => {
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }, 100);

  } catch (error) {
    console.error("下载失败:", error);
    document.getElementById("result").textContent = "CSV 下载失败！";
  }
}

// 渲染表格
function renderTable(data) {
  task = data.result;
  document.getElementById("task_id").innerHTML = task.task_id;
  document.getElementById("task_desc").innerHTML = task.task_desc;
  document.getElementById("status").innerHTML = task.status;
  document.getElementById("model_id").innerHTML = `<td><a href="/get_model.html?model_id=${task.model_id}">${task.model_id}</a></td>`;
  document.getElementById("model_label").innerHTML = formatJson(
    JSON.parse(task.model_label)
  );
  document.getElementById("error_message").innerHTML = task.error_message;
  document.getElementById("start_date").innerHTML = task.start_date;
  document.getElementById("end_date").innerHTML = task.end_date;
  resultElement = document.getElementById("result");
  if (task.result) {
    resultElement.innerHTML = "<a href='#'>下载 CSV</a>";
    resultElement.addEventListener("click", () => {
      createCSVDownloadLink(task.result, `${task_id}.csv`);
    });
  } else {
    {
      resultElement.innerHTML = "没有结果可供下载";
    }
  }
}

// 页面加载时获取数据
document.addEventListener("DOMContentLoaded", () => {
  const errorElement = document.getElementById("error");
  const deleteLink = document.getElementById("delete_task");
  deleteLink.href = `/delete_task.html?task_id=${task_id}`

  fetchDataFromAPI()
    .then((data) => {
      renderTable(data);
    })
    .catch((error) => {
      errorElement.style.display = "block";
      errorElement.textContent = `加载失败: ${error.log_id} ${error.error}`;
    });
});
