/** Poll /api/dashboard/ and refresh standings + feed without full reload. */
(function () {
  var POLL_MS = 5000;
  var lastRevision = null;

  function slugify(text) {
    return String(text).toLowerCase().replace(/\s+/g, "-");
  }

  function renderStandings(standings) {
    var list = document.getElementById("dashboard-leaderboard");
    if (!list) return;
    if (!standings.length) {
      list.innerHTML = '<li class="empty-state">Add household members to start the competition.</li>';
      return;
    }
    list.innerHTML = standings.map(function (row) {
      return (
        '<li class="leaderboard__row">' +
          '<div class="leaderboard__avatar" aria-hidden="true">' +
            '<span class="leaderboard__initials">' + row.initial + '</span>' +
          '</div>' +
          '<div class="leaderboard__info">' +
            '<span class="leaderboard__name">' + row.name + '</span>' +
            '<span class="leaderboard__xp">' + row.xp + ' XP</span>' +
            '<div class="leaderboard__progress" role="progressbar" aria-valuenow="' + row.progress_vs_leader + '" aria-valuemin="0" aria-valuemax="100">' +
              '<div class="leaderboard__progress-fill" style="width: ' + row.progress_vs_leader + '%;"></div>' +
            '</div>' +
          '</div>' +
        '</li>'
      );
    }).join("");
  }

  function renderFeed(feed) {
    var list = document.getElementById("dashboard-feed");
    if (!list) return;
    if (!feed.length) {
      list.innerHTML = '<li class="empty-state">No chores logged yet this week.</li>';
      return;
    }
    list.innerHTML = feed.map(function (item) {
      var badgeClass = "activity-feed__badge activity-feed__badge--" + slugify(item.status_label);
      return (
        '<li class="activity-feed__item">' +
          '<div class="activity-feed__body">' +
            '<span class="activity-feed__title">' + item.title + '</span>' +
            '<span class="activity-feed__meta">' + item.assignee_name + ' · ' + item.xp_value + ' XP</span>' +
          '</div>' +
          '<span class="' + badgeClass + '">' + item.status_label + '</span>' +
        '</li>'
      );
    }).join("");
  }

  function applyPayload(data) {
    if (data.revision === lastRevision) return;
    lastRevision = data.revision;

    var stake = document.getElementById("dashboard-stake-title");
    if (stake) {
      stake.textContent = data.stake_title || "No stake selected yet";
      stake.classList.toggle("stake-banner__title--empty", !data.stake_title);
    }
    var countdown = document.getElementById("dashboard-countdown");
    if (countdown) countdown.textContent = data.countdown;

    renderStandings(data.standings || []);
    renderFeed(data.feed || []);
  }

  function poll() {
    fetch("/api/dashboard/", { credentials: "same-origin" })
      .then(function (response) { return response.json(); })
      .then(applyPayload)
      .catch(function () {});
  }

  document.addEventListener("DOMContentLoaded", function () {
    poll();
    window.setInterval(poll, POLL_MS);
  });
})();
