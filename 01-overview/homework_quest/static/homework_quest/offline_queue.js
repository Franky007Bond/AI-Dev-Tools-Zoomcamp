/**
 * Offline queue for log/approve POSTs (localStorage).
 * See homework_quest/offline_queue.py for payload schema.
 */
(function (global) {
  var STORAGE_KEY = "homework_quest_offline_queue_v1";

  function loadQueue() {
    try {
      var raw = global.localStorage.getItem(STORAGE_KEY);
      if (!raw) return { version: 1, items: [] };
      var parsed = JSON.parse(raw);
      if (!parsed.items) parsed.items = [];
      parsed.version = 1;
      return parsed;
    } catch (err) {
      return { version: 1, items: [] };
    }
  }

  function saveQueue(queue) {
    global.localStorage.setItem(STORAGE_KEY, JSON.stringify(queue));
  }

  function enqueue(item) {
    var queue = loadQueue();
    var entry = {
      id: String(Date.now()) + "-" + String(Math.random()).slice(2, 8),
      kind: item.kind,
      url: item.url,
      method: "POST",
      contentType: item.contentType,
      body: item.body,
      createdAt: new Date().toISOString(),
    };
    queue.items.push(entry);
    saveQueue(queue);
    return entry;
  }

  function sendItem(item) {
    if (item.contentType === "json") {
      return fetch(item.url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item.body),
      });
    }
    var formData = new FormData();
    Object.keys(item.body).forEach(function (key) {
      formData.append(key, item.body[key]);
    });
    return fetch(item.url, {
      method: "POST",
      body: formData,
      credentials: "same-origin",
    });
  }

  function flush() {
    if (!global.navigator.onLine) {
      return Promise.resolve({ sent: 0, remaining: loadQueue().items.length });
    }
    var queue = loadQueue();
    var remaining = [];
    var sent = 0;
    var chain = Promise.resolve();

    queue.items.forEach(function (item) {
      chain = chain.then(function () {
        return sendItem(item).then(function (response) {
          if (response.ok || response.redirected || response.status === 302) {
            sent += 1;
          } else {
            remaining.push(item);
          }
        }).catch(function () {
          remaining.push(item);
        });
      });
    });

    return chain.then(function () {
      saveQueue({ version: 1, items: remaining });
      return { sent: sent, remaining: remaining.length };
    });
  }

  function queueOrSend(request, onSuccess, onQueued, onError) {
    if (!global.navigator.onLine) {
      enqueue(request);
      if (onQueued) onQueued();
      return Promise.resolve(false);
    }
    return sendItem(request)
      .then(function (response) {
        if (response.ok || response.redirected || response.status === 302) {
          if (onSuccess) onSuccess(response);
          return true;
        }
        enqueue(request);
        if (onQueued) onQueued();
        return false;
      })
      .catch(function () {
        enqueue(request);
        if (onQueued) onQueued();
        return false;
      });
  }

  global.HomeworkQuestOfflineQueue = {
    STORAGE_KEY: STORAGE_KEY,
    loadQueue: loadQueue,
    enqueue: enqueue,
    flush: flush,
    queueOrSend: queueOrSend,
  };

  global.addEventListener("online", function () {
    flush();
  });

  document.addEventListener("DOMContentLoaded", function () {
    flush();
  });
})(window);
