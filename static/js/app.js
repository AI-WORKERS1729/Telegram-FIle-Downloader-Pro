let phone = "";
let phoneCodeHash = ""; // Store the phone_code_hash

async function login() {
  phone = document.getElementById("phone").value;
  const res = await fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  });

  if (res.ok) {
    const data = await res.json();
    phoneCodeHash = data.phone_code_hash; // Save the phone_code_hash
    document.getElementById("login-form").style.display = "none";
    document.getElementById("code-form").style.display = "block";
  } else {
    alert("Failed to send code. Please try again.");
  }
}

async function verify() {
  const code = document.getElementById("code").value;
  const res = await fetch("/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone, code, phone_code_hash: phoneCodeHash }),
  });

  if (res.ok) {
    document.getElementById("code-form").style.display = "none";
    document.getElementById("upload-section").style.display = "block";
    document.getElementById("logout-section").style.display = "block";
    listFiles();
  } else {
    const errorData = await res.json();
    if (errorData.error.includes("expired")) {
      alert("The confirmation code has expired. Please request a new code.");
    } else {
      alert("Verification failed. Please try again.");
    }
  }
}

async function resendCode() {
  const res = await fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone }),
  });

  if (res.ok) {
    const data = await res.json();
    phoneCodeHash = data.phone_code_hash; // Update the phone_code_hash
    alert("A new code has been sent to your phone.");
  } else {
    alert("Failed to resend the code. Please try again.");
  }
}

async function uploadFile() {
  const input = document.getElementById("fileInput");
  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  await fetch("/upload?phone=" + phone, {
    method: "POST",
    body: formData,
  });
  listFiles();
}

async function listFiles() {
  const res = await fetch("/list?phone=" + phone);
  const files = await res.json();
  const list = document.getElementById("file-list");
  list.innerHTML = "";
  files.forEach(f => {
    const item = document.createElement("div");
    item.textContent = f.name;
    list.appendChild(item);
  });
}

async function logout() {
  await fetch("/logout?phone=" + phone, { method: "POST" });
  location.reload();
}
