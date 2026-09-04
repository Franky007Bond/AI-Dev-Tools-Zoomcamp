/** Slot-machine perk wheel reveal on ceremony celebration. */
(function () {
  var body = document.body;
  if (!body || body.getAttribute("data-spin-wheel") !== "true") return;

  var display = document.getElementById("perk-wheel-display");
  if (!display) return;

  var titles = (body.getAttribute("data-perk-titles") || "")
    .split("|")
    .filter(Boolean);
  var revealed = body.getAttribute("data-revealed-perk") || "";
  if (!titles.length || !revealed) return;

  display.classList.add("perk-wheel__label--spinning");
  var tick = 0;
  var maxTicks = 28 + Math.floor(Math.random() * 10);
  var interval = setInterval(function () {
    display.textContent = titles[tick % titles.length];
    tick += 1;
    if (tick >= maxTicks) {
      clearInterval(interval);
      display.classList.remove("perk-wheel__label--spinning");
      display.textContent = revealed;
    }
  }, 90);
})();
