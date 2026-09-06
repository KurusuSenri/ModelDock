const urlParams = new URLSearchParams(window.location.search);
const task_id = urlParams.get("task_id");
const apiUrl = apiServer + "api/tasks/" + task_id + "/";

document.getElementById("task_id").textContent = task_id;

document.getElementById("confirmDelete").addEventListener("click", () => {
    fetch(apiUrl, {
        method: "DELETE",
        headers: {
            "Content-Type": "application/json",
            "Authorization": getCookie("access_token")
        }
    })
        .then(async (response) => {
            const data = await response.json();

            if (data.log_id !== 200) {
                throw { log_id: data.log_id, data };
            }
            return data;
        })
        .then((data) => {
            document.getElementById("result").textContent = "删除完成";
        })
        .catch((err) => {
            document.getElementById("result").textContent =
                "Error: " + err.log_id + " " + err.data.error;
        });
});