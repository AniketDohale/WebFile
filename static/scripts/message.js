document.addEventListener("DOMContentLoaded", () => {
    const messages = document.querySelectorAll(".flash-msg-item");

    messages.forEach(msg => {
        setTimeout(() => {
            msg.classList.add("hide");
            setTimeout(() => msg.remove(), 450);
        }, 3000);
    });
});