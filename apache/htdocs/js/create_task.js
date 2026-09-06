// 将文件转换为 Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(",")[1]); // 去掉 data:*/*;base64,
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(file);
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const params = new URLSearchParams(window.location.search);
    const value = params.get("model_id");

    document.getElementById("model_id").value = value;
});

document
    .getElementById("uploadForm")
    .addEventListener("submit", async function (e) {
        e.preventDefault();

        const task_csv = document.getElementById("task_csv").files[0];
        const model_id = document.getElementById("model_id").value;
        const task_desc = document.getElementById("task_desc").value;

        if (!task_csv) {
            alert("请上传 CSV 文件！");
            return;
        }

        try {
            const csv_content = await fileToBase64(task_csv);

            // 构造 payload
            const payload = {
                task_csv: csv_content,
                task_desc: task_desc,
                model_id: model_id
            };

            // 发送请求
            const apiUrl = apiServer + "api/models/" + model_id + "/tasks/";
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: getCookie("access_token"),
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json();
            if (data.log_id != 200) {
                document.getElementById("response").innerHTML =
                    "Error: " + data["log_id"] + " " + data["error"]
            } else {
                document.getElementById("response").innerHTML =
                    "上传成功！任务 ID: " + data["task_id"] +
                    "<br><a href='get_task.html?task_id=" + data["task_id"] + "'>查看任务详情</a>";
            }
        } catch (err) {
            console.error(err);
            alert("上传失败: " + err);
        }
    });