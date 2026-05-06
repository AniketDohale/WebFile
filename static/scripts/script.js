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

document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".flash-msg-item");

    messages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add("hide");
            setTimeout(() => msg.remove(), 450);
        }, 3000);
    });
});