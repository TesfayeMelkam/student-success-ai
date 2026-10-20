// Theme, sidebar, toasts. Kept small and dependency-free (besides Bootstrap's Toast).
const root = document.documentElement;
const safeStore = {
  get: (k) => { try { return localStorage.getItem(k); } catch { return null; } },
  set: (k, v) => { try { localStorage.setItem(k, v); } catch { /* storage blocked */ } },
};

document.getElementById("themeToggle")?.addEventListener("click", () => {
  const next = root.dataset.bsTheme === "dark" ? "light" : "dark";
  root.dataset.bsTheme = next;
  safeStore.set("ssai-theme", next);
});

const shell = document.getElementById("appShell");
if (shell && safeStore.get("ssai-sidebar") === "collapsed") shell.classList.add("collapsed");
document.getElementById("sidebarToggle")?.addEventListener("click", () => {
  shell.classList.toggle("collapsed");
  safeStore.set("ssai-sidebar", shell.classList.contains("collapsed") ? "collapsed" : "open");
});

export function toast(message, level = "info") {
  const colors = { success: "success", error: "danger", warning: "warning", info: "primary" };
  const el = document.createElement("div");
  el.className = `toast align-items-center text-bg-${colors[level] || "primary"} border-0`;
  el.setAttribute("role", "status");
  const body = document.createElement("div");
  body.className = "d-flex";
  const text = document.createElement("div");
  text.className = "toast-body";
  text.textContent = message; // textContent: never inject HTML
  body.append(text);
  el.append(body);
  document.getElementById("toasts").append(el);
  const t = new bootstrap.Toast(el, { delay: 5000 });
  el.addEventListener("hidden.bs.toast", () => el.remove());
  t.show();
}

document.querySelectorAll("#django-messages span").forEach((s) => toast(s.textContent, s.dataset.level));

// Style Django-rendered form widgets with Bootstrap classes.
document.querySelectorAll(".auth-form input:not([type=hidden]), .auth-form select, .auth-form textarea")
  .forEach((el) => el.classList.add("form-control"));
document.querySelectorAll(".auth-form > div, .auth-form form > div").forEach((d) => d.classList.add("mb-3"));
