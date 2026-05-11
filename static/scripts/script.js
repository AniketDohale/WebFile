// Function to open the rename modal
function triggerRename(oldName, index) {
    const modal = document.getElementById('renameModal');
    const input = document.getElementById('modal-rename-input');
    const indexStore = document.getElementById('modal-target-index');

    input.value = oldName;
    indexStore.value = index;

    modal.style.display = 'flex';

    // Focus the Input Automatically
    // setTimeout(() => input.select(), 100);
}

function submitRenameModal() {
    const index = document.getElementById('modal-target-index').value;
    const newName = document.getElementById('modal-rename-input').value.trim();
    if (!newName) {
        alert("Name Cannot be Empty");
        return;
    }
    const form = document.getElementById('rename-form-' + index);
    const hiddenInput = document.getElementById('new-name-' + index);
    hiddenInput.value = newName;
    form.submit();
}

function closeRenameModal() {
    document.getElementById('renameModal').style.display = 'none';
}

function triggerCreate(type) {
    let name = prompt(`Enter ${type} Name:`);
    if (name && name.trim() !== "") {
        if (type === 'folder') {
            document.getElementById('folder-name-input').value = name;
            document.getElementById('folder-form').submit();
        } else {
            document.getElementById('file-name-input').value = name;
            document.getElementById('file-form').submit();
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".flash-msg-item");

    messages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add("hide");
            setTimeout(() => msg.remove(), 450);
        }, 3000);
    });
});

document.addEventListener("click", function (e) {
    const clickedMenuBtn = e.target.closest(".menu-btn");

    // Close all other menus when clicking outside
    document.querySelectorAll(".menu").forEach(menu => {
        if (!menu.contains(e.target)) {
            menu.classList.remove("open");
            menu.classList.remove("open-up")
        }
    });

    if (clickedMenuBtn) {
        const menu = clickedMenuBtn.closest(".menu");
        const dropdown = menu.querySelector(".menu-dropdown");
        const isOpen = menu.classList.toggle("open");

        if (isOpen) {
            // Check if the menu is near the bottom of the screen
            const rect = menu.getBoundingClientRect();
            const spaceBelow = window.innerHeight - rect.bottom;
            const dropdownHeight = 150;

            if (spaceBelow < dropdownHeight) {
                menu.classList.add("open-up");
            } else {
                menu.classList.remove("open-up");
            }
        }
    }
});

document.addEventListener("DOMContentLoaded", () => {

    let currentUploadXHR = null;

    const uploadBtn = document.getElementById("upload-btn");
    const cancelUploadBtn = document.getElementById("cancel-upload-btn");
    uploadBtn.addEventListener("click", uploadFile);

    cancelUploadBtn.addEventListener(
        "click",
        () => {

            if (currentUploadXHR) {
                currentUploadXHR.abort();
            }

        }
    );

    function resetUploadUI(container) {
        uploadBtn.disabled = false;
        cancelUploadBtn.style.display = "none";
        container.style.display = "none";
        currentUploadXHR = null;
    }

    function uploadFile() {
        const fileInput = document.getElementById("file-input");
        const path = document.getElementById("upload-path").value;
        if (fileInput.files.length === 0) {
            alert("Please Select a File First.");
            return;
        }

        const file = fileInput.files[0];
        const xhr = new XMLHttpRequest();
        currentUploadXHR = xhr;
        const container = document.getElementById("progress-container");
        const progressText = document.getElementById("progress-text");
        const uploadedSizeText = document.getElementById("uploaded-size");
        const totalSizeText = document.getElementById("total-size");
        const timeRemainingText = document.getElementById("time-remaining");

        container.style.display = "block";
        uploadBtn.disabled = true;
        cancelUploadBtn.style.display = "flex";
        const startTime = Date.now();

        xhr.upload.onprogress = function (e) {

            if (!e.lengthComputable) return;

            const percentComplete =
                Math.round((e.loaded / e.total) * 100);
            const loadedMB =
                (e.loaded / (1024 * 1024)).toFixed(2);
            const totalMB =
                (e.total / (1024 * 1024)).toFixed(2);
            const elapsed =
                (Date.now() - startTime) / 1000;
            const speed =
                e.loaded / elapsed;
            const remaining =
                (e.total - e.loaded) / speed;
            progressText.innerHTML =
                percentComplete + "%";
            uploadedSizeText.innerHTML =
                loadedMB + " MB";
            totalSizeText.innerHTML =
                totalMB + " MB";
            if (percentComplete < 100) {
                if (remaining > 60) {
                    timeRemainingText.innerHTML =
                        Math.round(remaining / 60) +
                        " min remaining";
                } else {
                    timeRemainingText.innerHTML =
                        Math.round(remaining) +
                        " sec remaining";
                }
            } else {
                progressText.innerHTML =
                    "Finalizing...";
                timeRemainingText.innerHTML =
                    "Completing upload...";
            }
        };

        xhr.onload = function () {
            uploadBtn.disabled = false;
            if (xhr.status === 200) {
                document.getElementById("cancel-upload-btn").style.display = "none";
                progressText.innerHTML = "100%";

                timeRemainingText.innerHTML =
                    "Upload Complete";
                setTimeout(() => {
                    const targetUrl =
                        path ? `/${path}` : `/`;
                    window.location.href =
                        targetUrl;
                }, 500);
            } else {
                alert(xhr.responseText);
                container.style.display = "none";
            }
        };

        xhr.onabort = function () {
            alert("Upload Cancelled");
            resetUploadUI(container);
        };

        xhr.onerror = function () {
            alert("Upload Failed");
            resetUploadUI(container);
        };

        xhr.open(
            "POST",
            "/upload?path=" + encodeURIComponent(path),
            true
        );

        xhr.setRequestHeader(
            "X-Filename",
            file.name
        );

        xhr.setRequestHeader(
            "Content-Type",
            "application/octet-stream"
        );

        xhr.send(file);
    }
});

async function showFileInfo(filePath) {
    const modal = document.getElementById('infoModal');

    try {
        const response = await fetch(`/info/${filePath}`);
        if (!response.ok) throw new Error("Could Not Fetch File Info");

        const data = await response.json();

        // Populate the modal fields
        document.getElementById('info-name').textContent = data.name;
        document.getElementById('info-type').textContent = data.type;
        document.getElementById('info-size').textContent = data.size;
        document.getElementById('info-created').textContent = data.created;
        document.getElementById('info-modified').textContent = data.modified;
        document.getElementById('info-extension').textContent = data.extension;

        // Show the modal
        modal.style.display = 'flex';

    } catch (error) {
        alert("Error: " + error.message);
    }
}

// Function to close the modal
function closeModal() {
    document.getElementById('infoModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close Modal if User Clicks anywhere Outside of the Modal
window.onclick = function (event) {
    const infoModal = document.getElementById('infoModal');
    const renameModal = document.getElementById('renameModal');

    if (event.target == infoModal) {
        closeModal();
    }
    if (event.target == renameModal) {
        closeRenameModal();
    }
}

let currentUploadXHR = null;
const pasteForm = document.getElementById("paste-form");

if (pasteForm) {

    let currentPasteTaskId = null;
    let pasteInterval = null;

    const progressBox =
        document.getElementById("paste-progress");

    const progressText =
        document.getElementById("paste-progress-text");

    const cancelPasteBtn =
        document.getElementById("cancel-paste-btn");

    pasteForm.addEventListener("submit", async function (e) {
        e.preventDefault();

        const formData = new FormData(pasteForm);
        const response = await fetch("/paste", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        const taskId = data.task_id;
        currentPasteTaskId = taskId;

        progressBox.style.display = "block";
        cancelPasteBtn.style.display = "flex";

        pasteInterval = setInterval(async () => {

            const res = await fetch(`/progress/${taskId}`);
            const progressData = await res.json();

            progressText.innerText =
                `${progressData.progress || 0}%`;

            if (progressData.status === "completed") {
                clearInterval(pasteInterval);
                pasteInterval = null;

                progressText.innerText = "Completed";
                cancelPasteBtn.style.display = "none";

                location.reload();
            }

            if (progressData.status === "error") {
                clearInterval(pasteInterval);
                pasteInterval = null;

                progressText.innerText = "Error";
                cancelPasteBtn.style.display = "none";
            }

            if (progressData.status === "cancelled") {
                clearInterval(pasteInterval);
                pasteInterval = null;

                progressText.innerText = "Cancelled";
                cancelPasteBtn.style.display = "none";
            }

        }, 500);
    });

    cancelPasteBtn.addEventListener("click", async () => {

        if (!currentPasteTaskId) return;

        await fetch(`/cancel-task/${currentPasteTaskId}`, {
            method: "POST"
        });

        if (pasteInterval) {
            clearInterval(pasteInterval);
            pasteInterval = null;
        }

        progressText.innerText = "Cancelled";
        cancelPasteBtn.style.display = "none";
    });
}

// List and Grid Toggle
const fileList = document.getElementById("file-list");
const layoutToggle = document.getElementById("layout-toggle");
const layoutIcon = document.getElementById("layout-icon");

function applyLayout() {
    const savedLayout = localStorage.getItem("layout");
    const htmlEl = document.documentElement;

    if (savedLayout === "grid") {
        fileList.classList.add("grid-view");
        htmlEl.classList.add("grid-layout-active");
        layoutIcon.src = "/static/icons/list.png";
    } else {
        fileList.classList.remove("grid-view");
        htmlEl.classList.remove("grid-layout-active");
        layoutIcon.src = "/static/icons/grid.png";
    }
}

applyLayout();

window.addEventListener("pageshow", applyLayout);

layoutToggle.addEventListener("click", () => {
    const isCurrentlyGrid = fileList.classList.contains("grid-view");
    if (isCurrentlyGrid) {
        localStorage.setItem("layout", "list");
        document.documentElement.classList.remove("grid-layout-active");
    } else {
        localStorage.setItem("layout", "grid");
        document.documentElement.classList.add("grid-layout-active");
    }
    applyLayout();
});

// Make File Rows Clickable except Menu
document.addEventListener("click", function (e) {
    if (e.target.closest(".menu")) {
        return;
    }
    if (e.target.closest("a")) {
        return;
    }
    const row = e.target.closest(".file-row");
    if (row && row.dataset.href) {
        window.location.href = row.dataset.href;
    }
});

const cancelUploadBtn = document.getElementById("cancel-upload-btn");

cancelUploadBtn.addEventListener("click", () => {
    if (currentUploadXHR) {
        currentUploadXHR.abort();
    }
});