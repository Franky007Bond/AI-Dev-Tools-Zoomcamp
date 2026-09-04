/**
 * Global PIN overlay: pick profile → enter PIN → run intercepted action.
 * Never logs or stores PINs beyond in-memory submission.
 */
(function () {
  var overlay = document.getElementById("pin-overlay");
  if (!overlay) return;

  var profileStep = overlay.querySelector('[data-step="profile"]');
  var pinStep = overlay.querySelector('[data-step="pin"]');
  var titleEl = document.getElementById("pin-overlay-title");
  var pinDots = overlay.querySelectorAll(".pin-overlay__pin-dot");
  var errorEl = overlay.querySelector("[data-pin-error]");

  var pendingAction = null;
  var selectedProfileId = null;
  var pinDigits = "";

  function getCsrfToken() {
    var input = overlay.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function showError(message) {
    if (!errorEl) return;
    if (message) {
      errorEl.textContent = message;
      errorEl.hidden = false;
    } else {
      errorEl.textContent = "";
      errorEl.hidden = true;
    }
  }

  function resetPinEntry() {
    pinDigits = "";
    pinDots.forEach(function (dot) {
      dot.setAttribute("data-filled", "false");
    });
    showError("");
  }

  function showStep(step) {
    if (step === "profile") {
      profileStep.hidden = false;
      pinStep.hidden = true;
      if (titleEl) titleEl.textContent = "Who are you?";
      overlay.querySelectorAll(".pin-overlay__profile").forEach(function (btn) {
        btn.classList.remove("pin-overlay__profile--selected");
      });
    } else {
      profileStep.hidden = true;
      pinStep.hidden = false;
      if (titleEl) titleEl.textContent = "Enter your PIN";
      resetPinEntry();
    }
  }

  function openOverlay(action) {
    pendingAction = action;
    selectedProfileId = null;
    resetPinEntry();
    showStep("profile");
    overlay.hidden = false;
    overlay.setAttribute("aria-hidden", "false");
  }

  function closeOverlay() {
    overlay.hidden = true;
    overlay.setAttribute("aria-hidden", "true");
    pendingAction = null;
    selectedProfileId = null;
    resetPinEntry();
    showStep("profile");
  }

  function updatePinDisplay() {
    pinDots.forEach(function (dot, index) {
      dot.setAttribute("data-filled", index < pinDigits.length ? "true" : "false");
    });
  }

  function appendDigit(digit) {
    if (pinDigits.length >= 4) return;
    pinDigits += digit;
    updatePinDisplay();
    if (pinDigits.length === 4) {
      submitAction();
    }
  }

  function submitAction() {
    if (!pendingAction || !selectedProfileId || pinDigits.length !== 4) return;

    var kind = pendingAction.kind;
    if (kind === "approve") {
      submitApprove();
    } else if (kind === "log-routine" || kind === "log-bounty") {
      submitFormPost();
    }
  }

  function submitApprove() {
    var url = pendingAction.approveUrl;
    var request = {
      kind: "approve",
      url: url,
      contentType: "json",
      body: {
        approver_id: parseInt(selectedProfileId, 10),
        pin: pinDigits,
      },
    };

    function onSuccess() {
      if (window.HomeworkQuestArcade) {
        window.HomeworkQuestArcade.playApproveSound();
        window.HomeworkQuestArcade.launchConfetti(1200);
      }
      window.setTimeout(function () {
        window.location.href = "/?approved=1";
      }, 350);
    }

    if (window.HomeworkQuestOfflineQueue) {
      window.HomeworkQuestOfflineQueue.queueOrSend(
        request,
        onSuccess,
        function () {
          showError("Saved offline — will retry when back online.");
          resetPinEntry();
        },
        function () {
          showError("Network error. Try again.");
          resetPinEntry();
        }
      );
      return;
    }

    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request.body),
    })
      .then(function (response) {
        return response.json().then(function (body) {
          return { ok: response.ok, body: body };
        });
      })
      .then(function (result) {
        if (result.ok) {
          onSuccess();
          return;
        }
        showError(result.body.error || "Could not complete action.");
        resetPinEntry();
      })
      .catch(function () {
        showError("Network error. Try again.");
        resetPinEntry();
      });
  }

  function submitFormPost() {
    var request = {
      kind: "log-form",
      url: pendingAction.postUrl,
      contentType: "form",
      body: {
        profile_id: selectedProfileId,
        pin: pinDigits,
        csrfmiddlewaretoken: getCsrfToken(),
      },
    };

    function onSuccess(response) {
      window.location.href = (response && response.url) || "/";
    }

    if (window.HomeworkQuestOfflineQueue) {
      window.HomeworkQuestOfflineQueue.queueOrSend(
        request,
        onSuccess,
        function () {
          showError("Saved offline — will retry when back online.");
          resetPinEntry();
        },
        function () {
          showError("Network error. Try again.");
          resetPinEntry();
        }
      );
      return;
    }

    var formData = new FormData();
    formData.append("profile_id", selectedProfileId);
    formData.append("pin", pinDigits);
    formData.append("csrfmiddlewaretoken", getCsrfToken());

    fetch(pendingAction.postUrl, {
      method: "POST",
      body: formData,
      credentials: "same-origin",
    })
      .then(function (response) {
        if (response.ok || response.redirected || response.status === 302) {
          onSuccess(response);
          return;
        }
        showError("Could not complete action.");
        resetPinEntry();
      })
      .catch(function () {
        showError("Network error. Try again.");
        resetPinEntry();
      });
  }

  document.addEventListener("click", function (event) {
    var trigger = event.target.closest("[data-pin-overlay]");
    if (!trigger) return;

    event.preventDefault();
    openOverlay({
      kind: trigger.getAttribute("data-pin-overlay"),
      approveUrl: trigger.getAttribute("data-approve-url"),
      postUrl: trigger.getAttribute("data-post-url"),
    });
  });

  overlay.querySelectorAll("[data-pin-overlay-close]").forEach(function (el) {
    el.addEventListener("click", closeOverlay);
  });

  overlay.querySelectorAll("[data-profile-id]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      selectedProfileId = btn.getAttribute("data-profile-id");
      overlay.querySelectorAll(".pin-overlay__profile").forEach(function (b) {
        b.classList.remove("pin-overlay__profile--selected");
      });
      btn.classList.add("pin-overlay__profile--selected");
      showStep("pin");
    });
  });

  overlay.querySelectorAll("[data-digit]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      appendDigit(btn.getAttribute("data-digit"));
    });
  });

  var backBtn = overlay.querySelector("[data-pin-back]");
  if (backBtn) {
    backBtn.addEventListener("click", function () {
      if (pinDigits.length) {
        pinDigits = pinDigits.slice(0, -1);
        updatePinDisplay();
      }
    });
  }

  var clearBtn = overlay.querySelector("[data-pin-clear]");
  if (clearBtn) {
    clearBtn.addEventListener("click", resetPinEntry);
  }

  var backProfilesBtn = overlay.querySelector("[data-pin-back-profiles]");
  if (backProfilesBtn) {
    backProfilesBtn.addEventListener("click", function () {
      showStep("profile");
    });
  }
})();
