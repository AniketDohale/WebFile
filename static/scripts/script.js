function triggerRename(oldName, index) {
    let newName = prompt("Rename '" + oldName + "' to:", oldName);

    if (newName === null || newName.trim() === "" || newName === oldName) {
        return
    }
    const form = document.getElementById('rename-form-' + index);
    const hiddenInput = document.getElementById('new-name-' + index);
    hiddenInput.value = newName.trim();
    form.submit();
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
    try {
        const response = await fetch(`/info/${filePath}`);
        if (!response.ok) throw new Error("Could Not Fetch File Info");
        
        const data = await response.json();
        
        const details = `
            Name: ${data.name}
            Type: ${data.type}
            Size: ${data.size}
            Created: ${data.created}
            Modified: ${data.modified}
            Extension: ${data.extension}
        `;
        
        alert(details);
    } catch (error) {
        alert("Error: " + error.message);
    }
}