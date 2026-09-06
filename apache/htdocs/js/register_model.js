const apiUrl = apiServer + "api/models/";

// 将文件转换为 Base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(",")[1]); // 去掉 data:*/*;base64,
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(file);
    });
}

document
    .getElementById("uploadForm")
    .addEventListener("submit", async function (e) {
        e.preventDefault();

        const modelFile = document.getElementById("modelFile").files[0];
        const pipelineFile = document.getElementById("pipelineFile").files[0];
        const modelLabel = document.getElementById("modelLabel").value;
        const modelColumn = document.getElementById("modelColumn").value;
        const modelDesc = document.getElementById("modelDesc").value;
        const modelType = document.getElementById("modelType").value;

        if (!modelFile) {
            alert("请上传模型文件！");
            return;
        }

        try {
            const modelContent = await fileToBase64(modelFile);
            let pipelineContent = null;
            if (pipelineFile) {
                pipelineContent = await fileToBase64(pipelineFile);
            }

            // 构造 payload
            const payload = {
                model_content: modelContent,
                model_label: modelLabel,
                model_column: JSON.parse(modelColumn),
                model_desc: modelDesc,
                model_type: modelType,
            };
            if (pipelineContent) {
                payload.pipeline_content = pipelineContent;
            }

            // 发送请求
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
                    "上传成功！模型 ID: " + data["model_id"] +
                    "<br><a href='get_model.html?model_id=" + data["model_id"] + "'>查看模型详情</a>";
            }
        } catch (err) {
            console.error(err);
            alert("上传失败: " + err);
        }
    });