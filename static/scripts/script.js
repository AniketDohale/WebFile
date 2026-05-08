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

document.getElementById('upload-form').addEventListener('submit', function (e) {
    e.preventDefault();
    uploadFile();
});

function uploadFile() {
    const fileInput = document.getElementById('file-input');
    const path = document.getElementById('upload-path').value;

    if (fileInput.files.length === 0) {
        alert("Please select a file first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    formData.append("path", path);

    const xhr = new XMLHttpRequest();
    const container = document.getElementById('progress-container');
    const progressText = document.getElementById('progress-text');

    // New Elements
    const uploadedSizeText = document.getElementById('uploaded-size');
    const totalSizeText = document.getElementById('total-size');
    const timeRemainingText = document.getElementById('time-remaining');

    container.style.display = 'block';

    // Track start time
    const startTime = new Date().getTime();

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percentComplete = Math.round((e.loaded / e.total) * 100);

            const loadedMB = (e.loaded / (1024 * 1024)).toFixed(2);
            const totalMB = (e.total / (1024 * 1024)).toFixed(2);

            const currentTime = new Date().getTime();
            const durationInSeconds = (currentTime - startTime) / 1000;
            const bitsPerSecond = e.loaded / durationInSeconds;
            const remainingBytes = e.total - e.loaded;
            const secondsRemaining = remainingBytes / bitsPerSecond;

            progressText.innerHTML = percentComplete + '%';
            uploadedSizeText.innerHTML = loadedMB + ' MB';
            totalSizeText.innerHTML = totalMB + ' MB';

            if (percentComplete < 100) {
                timeRemainingText.innerHTML = "Time Remaining: " + formatTime(secondsRemaining);
            } else {
                progressText.innerHTML = 'Saving File...';
                timeRemainingText.innerHTML = "Upload Complete, Server Processing...";
            }
        }
    };

    // Helper function to format seconds into MM:SS
    function formatTime(seconds) {
        if (!isFinite(seconds) || seconds < 0) return "Calculating...";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}m ${secs}s`;
    }

    // Handle Completion
    xhr.onload = function () {
        if (xhr.status === 200) {
            progressText.innerHTML = '100%';
            timeRemainingText.innerHTML = "Upload Successful! Finalizing...";

            const targetUrl = path ? `/${path}` : `/`;

            setTimeout(function () {
                window.location.href = targetUrl;
            }, 500);
        } else {
            alert("Upload Failed. Error Code: " + xhr.status);
            container.style.display = 'none';
        }
    };

    xhr.onerror = function () {
        alert("An Error Occurred during the Upload.");
        container.style.display = 'none';
    };
    xhr.open("POST", "/upload", true);
    xhr.send(formData);
}

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

const pasteForm = document.getElementById("paste-form");
if (pasteForm) {
    pasteForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const formData = new FormData(pasteForm);
        const response = await fetch("/paste", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        const taskId = data.task_id;
        const progressBox = document.getElementById("paste-progress");
        const progressText = document.getElementById("paste-progress-text");

        progressBox.style.display = "block";

        const interval = setInterval(async () => {
            const res = await fetch(`/progress/${taskId}`);
            const progressData = await res.json();
            progressText.innerText =
                `${progressData.progress || 0}%`;

            if (
                progressData.status === "completed"
            ) {
                clearInterval(interval);
                progressText.innerText = "Completed";
                location.reload();
            }

            if (
                progressData.status === "error"
            ) {
                clearInterval(interval);
                progressText.innerText =
                    "Error";
            }
        }, 500);
    });
}