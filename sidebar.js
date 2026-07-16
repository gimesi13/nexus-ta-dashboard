(function () {
  "use strict";
  var app = document.querySelector(".app");
  var toggle = document.getElementById("nav-toggle");
  var backdrop = document.getElementById("nav-backdrop");
  if (!app || !toggle) return;

  function close() { app.classList.remove("nav-open"); }

  toggle.addEventListener("click", function () {
    app.classList.toggle("nav-open");
  });
  if (backdrop) backdrop.addEventListener("click", close);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });
  app.querySelectorAll(".nav-item").forEach(function (a) {
    a.addEventListener("click", close);
  });
})();
