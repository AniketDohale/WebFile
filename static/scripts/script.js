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

document.addEventListener("click", function (e) {
    const clickedMenuBtn = e.target.closest(".menu-btn");
    
    // Close all other menus when clicking outside
    document.querySelectorAll(".menu").forEach(menu => {
        if (!menu.contains(e.target)) {
            menu.classList.remove("open");
            menu.classList.remove("open-up"); // Reset position
        }
    });

    if (clickedMenuBtn) {
        const menu = clickedMenuBtn.closest(".menu");
        const dropdown = menu.querySelector(".menu-dropdown");
        
        // Toggle the 'open' class
        const isOpen = menu.classList.toggle("open");

        if (isOpen) {
            // Check if the menu is near the bottom of the screen
            const rect = menu.getBoundingClientRect();
            const spaceBelow = window.innerHeight - rect.bottom;
            const dropdownHeight = 150; // Approximate height of your menu

            if (spaceBelow < dropdownHeight) {
                menu.classList.add("open-up");
            } else {
                menu.classList.remove("open-up");
            }
        }
    }
});