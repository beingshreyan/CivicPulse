document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("cp-hamburger");
  const navMenu = document.querySelector("[data-cp-nav]");

  if (!toggleBtn || !navMenu) return;

  const setMenuState = (open) => {
    navMenu.classList.toggle("is-open", open);
    toggleBtn.setAttribute("aria-expanded", String(open));
  };

  toggleBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    const isOpen = toggleBtn.getAttribute("aria-expanded") === "true";
    setMenuState(!isOpen);
  });

  navMenu.querySelectorAll("a, button").forEach((item) => {
    item.addEventListener("click", () => {
      if (window.innerWidth <= 768) {
        setMenuState(false);
      }
    });
  });

  document.addEventListener("click", (e) => {
    if (!navMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
      setMenuState(false);
    }
  });

  window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
      setMenuState(false);
    }
  });
});