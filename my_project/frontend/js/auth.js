let isRegister = true;

function toggleForm() {
  isRegister = !isRegister;
  document.getElementById("form-title").textContent = isRegister ? "Register" : "Login";
  document.getElementById("email").style.display = isRegister ? "block" : "none";
  document.querySelector(".switch").textContent = isRegister
    ? "Already have an account? Login"
    : "Don't have an account? Register";
}

document.getElementById("auth-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const email = document.getElementById("email").value;

  const payload = isRegister ? { username, password, email } : { username, password };

  const backendUrl = "http://127.0.0.1:8080"; // ✅ 根据实际 IP/Port 修改
  const endpoint = isRegister ? `${backendUrl}/user` : `${backendUrl}/login`;

  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.status === "success") {
      alert("✅ " + data.message);
      localStorage.setItem("user_id", data.user_id);
      window.location.href = "/dashboard.html";
    } else {
      alert("❌ " + (data.message || "Login failed"));
    }
  } catch (err) {
    console.error(err);
    alert("Request failed");
  }
});
