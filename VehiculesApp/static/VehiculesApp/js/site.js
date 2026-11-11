document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.querySelector(".menu-toggle");
  const navigation = document.querySelector("#main-nav");

  if (menuToggle && navigation) {
    menuToggle.addEventListener("click", () => {
      const isExpanded = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!isExpanded));
      menuToggle.setAttribute(
        "aria-label",
        isExpanded ? "Ouvrir le menu" : "Fermer le menu",
      );
      navigation.classList.toggle("is-open", !isExpanded);
    });
  }

  const currentPath = window.location.pathname.replace(/\/+$/, "") || "/";
  document.querySelectorAll(".site-nav a").forEach((link) => {
    const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/+$/, "") || "/";
    if (linkPath === currentPath) {
      link.setAttribute("aria-current", "page");
    }
  });
});
