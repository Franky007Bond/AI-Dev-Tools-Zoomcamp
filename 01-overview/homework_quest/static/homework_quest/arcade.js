/**
 * Homework Quest arcade feedback — Web Audio SFX + confetti.
 * Falls back silently when AudioContext is blocked (autoplay policy).
 */
(function (global) {
  var audioContext = null;

  function getAudioContext() {
    if (audioContext) return audioContext;
    var AudioCtx = global.AudioContext || global.webkitAudioContext;
    if (!AudioCtx) return null;
    try {
      audioContext = new AudioCtx();
      return audioContext;
    } catch (err) {
      return null;
    }
  }

  function playTone(frequency, durationMs, type) {
    var ctx = getAudioContext();
    if (!ctx) return;
    try {
      if (ctx.state === "suspended") {
        ctx.resume().catch(function () {});
      }
      var oscillator = ctx.createOscillator();
      var gain = ctx.createGain();
      oscillator.type = type || "square";
      oscillator.frequency.value = frequency;
      gain.gain.value = 0.08;
      oscillator.connect(gain);
      gain.connect(ctx.destination);
      oscillator.start();
      oscillator.stop(ctx.currentTime + durationMs / 1000);
    } catch (err) {
      /* Audio blocked or unavailable — XP logic must not depend on this. */
    }
  }

  function playApproveSound() {
    playTone(880, 90, "square");
    setTimeout(function () { playTone(1175, 120, "square"); }, 95);
  }

  function playWinSound() {
    [523, 659, 784, 1047].forEach(function (freq, index) {
      setTimeout(function () { playTone(freq, 140, "triangle"); }, index * 120);
    });
  }

  function launchConfetti(durationMs) {
    var canvas = document.getElementById("arcade-confetti");
    if (!canvas) return;
    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    canvas.width = global.innerWidth;
    canvas.height = global.innerHeight;

    var colors = ["#58a6ff", "#3fb950", "#d29922", "#f0883e", "#8957e5", "#ffa657"];
    var particles = [];
    for (var i = 0; i < 80; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: -20 - Math.random() * canvas.height * 0.3,
        size: 6 + Math.random() * 8,
        color: colors[Math.floor(Math.random() * colors.length)],
        vx: -3 + Math.random() * 6,
        vy: 2 + Math.random() * 5,
        rotation: Math.random() * Math.PI,
      });
    }

    var start = performance.now();
    function frame(now) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      particles.forEach(function (p) {
        p.x += p.vx;
        p.y += p.vy;
        p.vy += 0.08;
        p.rotation += 0.08;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rotation);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
        ctx.restore();
      });
      if (now - start < (durationMs || 1800)) {
        requestAnimationFrame(frame);
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }
    }
    requestAnimationFrame(frame);
  }

  function initFromDom() {
    var body = document.body;
    if (!body) return;
    if (body.getAttribute("data-celebration") === "true") {
      playWinSound();
      launchConfetti(2200);
    }
    if (body.getAttribute("data-approved") === "true") {
      playApproveSound();
      launchConfetti(1200);
    }
  }

  global.HomeworkQuestArcade = {
    playApproveSound: playApproveSound,
    playWinSound: playWinSound,
    launchConfetti: launchConfetti,
    initFromDom: initFromDom,
  };

  document.addEventListener("DOMContentLoaded", initFromDom);
})(window);
