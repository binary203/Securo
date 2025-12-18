const aiButton = document.getElementById("AiAssist");
const sendButton = document.getElementById("sendToAI");
const popup = document.getElementById("popup");
const closeBtn = document.getElementById("close");
const overlay = document.getElementById("overlay");

aiButton.addEventListener("click", () => {
    popup.classList.add("show");
    overlay.classList.add("show");
});

closeBtn.addEventListener("click", () => {
    popup.classList.remove("show");
    overlay.classList.remove("show");
});

overlay.addEventListener("click", (e) => {
    if (e.target === overlay) {
        popup.classList.remove("show");
        overlay.classList.remove("show");
    }
});