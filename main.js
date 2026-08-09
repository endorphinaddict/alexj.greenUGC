/* Mobile nav, work filtering, footer year. No dependencies. */
(function () {
  "use strict";

  /* ---- mobile nav ---- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
      toggle.textContent = open ? "Menu" : "Close";
    });
  }

  /* ---- work filter ---- */
  var buttons = document.querySelectorAll("[data-filter]");
  var grid = document.getElementById("grid");
  var empty = document.getElementById("empty");

  if (buttons.length && grid) {
    var items = grid.querySelectorAll("li");

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var want = btn.getAttribute("data-filter");
        var shown = 0;

        buttons.forEach(function (b) {
          b.setAttribute("aria-pressed", String(b === btn));
        });

        items.forEach(function (li) {
          var match = want === "all" || li.getAttribute("data-cat") === want;
          li.hidden = !match;
          if (match) shown++;
        });

        if (empty) empty.hidden = shown !== 0;
      });
    });
  }

  /* ---- footer year ---- */
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());
})();
