/** Effort slider XP preview (mirrors server xp_from_minutes for 5–60 min). */
(function () {
  function xpFromMinutes(minutes) {
    if (minutes <= 0) return 0;
    return Math.max(0, Math.round(10 + (minutes - 5) * (90 / 40)));
  }

  var slider = document.getElementById("bounty-minutes");
  if (!slider) return;

  var xpPreview = document.getElementById("bounty-xp-preview");
  var minutesLabel = document.getElementById("bounty-minutes-label");

  function updatePreview() {
    var minutes = parseInt(slider.value, 10);
    if (minutesLabel) minutesLabel.textContent = String(minutes);
    if (xpPreview) xpPreview.textContent = xpFromMinutes(minutes) + " XP";
  }

  slider.addEventListener("input", updatePreview);
  updatePreview();
})();
