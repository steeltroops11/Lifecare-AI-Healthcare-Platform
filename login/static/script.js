const roleButtons = document.querySelectorAll(".role-btn");
const roleInput = document.getElementById("roleInput");
const togglePassword = document.getElementById("togglePassword");
const passwordField = document.getElementById("passwordField");

roleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
        roleButtons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        roleInput.value = btn.dataset.role;
    });
});

if (togglePassword && passwordField) {
    togglePassword.addEventListener("click", () => {
        if (passwordField.type === "password") {
            passwordField.type = "text";
            togglePassword.innerHTML = '<i class="fa-regular fa-eye-slash"></i>';
        } else {
            passwordField.type = "password";
            togglePassword.innerHTML = '<i class="fa-regular fa-eye"></i>';
        }
    });
}