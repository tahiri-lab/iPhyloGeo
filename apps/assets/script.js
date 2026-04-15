// Direct DOM-based nav highlight for instant feedback
function updateNavHighlight() {
  var pathname = window.location.pathname;
  var linkMap = {
    "/": "nav-link-home",
    "/getStarted": "nav-link-getstarted",
    "/results": "nav-link-results",
    "/settings": "nav-link-settings",
    "/help": "nav-link-help",
  };
  var navIds = ["nav-link-home", "nav-link-getstarted", "nav-link-results"];
  var bottomIds = ["nav-link-settings", "nav-link-help"];

  // Check for exact match first, then check for /result/* pattern
  var activeId = linkMap[pathname] || "";
  if (!activeId && pathname.startsWith("/result/")) {
    activeId = "nav-link-results";
  }

  navIds.forEach(function (id) {
    var el = document.getElementById(id);
    if (el)
      el.className =
        id === activeId
          ? "nav-item nav-item-top selected"
          : "nav-item nav-item-top";
  });
  bottomIds.forEach(function (id) {
    var el = document.getElementById(id);
    if (el)
      el.className =
        id === activeId
          ? "nav-item nav-item-bottom selected"
          : "nav-item nav-item-bottom";
  });
}

// Intercept history.pushState and replaceState to catch all Dash navigations
(function () {
  var origPushState = history.pushState;
  var origReplaceState = history.replaceState;
  history.pushState = function () {
    origPushState.apply(this, arguments);
    setTimeout(updateNavHighlight, 0);
  };
  history.replaceState = function () {
    origReplaceState.apply(this, arguments);
    setTimeout(updateNavHighlight, 0);
  };
})();

// Handle browser back/forward
window.addEventListener("popstate", function () {
  setTimeout(updateNavHighlight, 0);
});

// Apply highlight when nav elements are available
(function () {
  var _updating = false;
  var ids = [
    "nav-link-home",
    "nav-link-getstarted",
    "nav-link-results",
    "nav-link-settings",
    "nav-link-help",
  ];

  var observer = new MutationObserver(function () {
    if (_updating) return;
    _updating = true;
    updateNavHighlight();
    _updating = false;
  });

  function startObserving() {
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el)
        observer.observe(el, { attributes: true, attributeFilter: ["class"] });
    });
  }

  var origUpdate = updateNavHighlight;
  updateNavHighlight = function () {
    observer.disconnect();
    origUpdate();
    startObserving();
  };

  // Detect when nav elements are added to the DOM
  var bodyObserver = new MutationObserver(function () {
    if (document.getElementById("nav-link-home")) {
      bodyObserver.disconnect();
      updateNavHighlight();
    }
  });

  if (document.body) {
    bodyObserver.observe(document.body, { childList: true, subtree: true });
  } else {
    document.addEventListener("DOMContentLoaded", function () {
      bodyObserver.observe(document.body, { childList: true, subtree: true });
    });
  }
})();

let open = true;

function responsiveNavbar() {
  const labContainer = document.getElementById("lab-container");
  const navBar = document.getElementById("nav-bar");
  const labName = document.getElementById("lab-name");
  const labBurger = document.getElementById("lab-burger");
  const themeSwitch = document.getElementById("theme-switch");
  const navLink = document.getElementById("nav-link");

  if (open) {
    if (labContainer) labContainer.classList.add("minimized");
    if (navBar) navBar.classList.add("minimized");
    if (labName) labName.classList.add("minimized");
    if (themeSwitch) themeSwitch.classList.add("minimized");
    if (navLink) navLink.classList.add("minimized");

    open = false;
  } else {
    if (labContainer) labContainer.classList.remove("minimized");
    if (navBar) navBar.classList.remove("minimized");
    if (labName) labName.classList.remove("minimized");
    if (themeSwitch) themeSwitch.classList.remove("minimized");
    if (navLink) navLink.classList.remove("minimized");

    open = true;
  }
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    navbar_function: function () {
      responsiveNavbar();

      // Wait for CSS transition to complete before resizing charts (avoid lags)
      const navbar = document.getElementById("nav-bar");
      if (navbar) {
        let handled = false;
        function handleTransitionEnd(e) {
          if (e.propertyName === "width" && !handled) {
            handled = true;
            navbar.removeEventListener("transitionend", handleTransitionEnd);
            requestAnimationFrame(function () {
              window.dispatchEvent(new Event("resize"));
            });
          }
        }
        navbar.addEventListener("transitionend", handleTransitionEnd);
        setTimeout(function () {
          if (!handled) {
            handled = true;
            navbar.removeEventListener("transitionend", handleTransitionEnd);
            window.dispatchEvent(new Event("resize"));
          }
        }, 500);
      }

      return "";
    },

    collapse_result_section_function: function (
      trigger,
      collapse_section,
      trigger_id,
    ) {
      if (trigger >= 1) {
        if (
          document
            .getElementById(collapse_section)
            .classList.contains("collapse-row")
        ) {
          document.getElementById(trigger_id).classList.remove("close");
          document
            .getElementById(collapse_section)
            .classList.remove("collapse-row");
        } else {
          document.getElementById(trigger_id).classList.add("close");
          document
            .getElementById(collapse_section)
            .classList.add("collapse-row");
        }
      }
      return "";
    },

    next_option_function: function (nextClicks, testClicks, desireDiv) {
      var callbackContext = window.dash_clientside.callback_context;
      if (!callbackContext || !callbackContext.triggered.length) {
        return "";
      }

      var triggeredProp = callbackContext.triggered[0].prop_id || "";
      var isNextTrigger = triggeredProp.indexOf("next-button.") === 0;
      var isDemoTrigger = triggeredProp.indexOf("upload-test-data.") === 0;

      // Ignore non-user triggers and stale n_clicks updates.
      if (!isNextTrigger && !isDemoTrigger) {
        return "";
      }
      if (isNextTrigger && (!nextClicks || nextClicks < 1)) {
        return "";
      }
      if (isDemoTrigger && (!testClicks || testClicks < 1)) {
        return "";
      }

      var targetId = desireDiv || "params-sections";
      var maxWaitMs = 2200;
      var startAt = Date.now();
      var observer = null;
      var fallbackTimer = null;
      var didScroll = false;

      function cleanup() {
        if (observer) {
          observer.disconnect();
          observer = null;
        }
        if (fallbackTimer) {
          clearTimeout(fallbackTimer);
          fallbackTimer = null;
        }
      }

      function tryScrollWhenReady() {
        if (didScroll) {
          return true;
        }

        var target = document.getElementById(targetId);

        if (!target) {
          return false;
        }

        // Wait until the params section has actually been rendered by Dash.
        var hasRenderedParams =
          !!document.getElementById("submit-dataset") ||
          !!target.querySelector(".parameters-section, .submit-section");

        if (!hasRenderedParams) {
          return false;
        }

        didScroll = true;
        target.scrollIntoView({ behavior: "smooth", block: "start" });

        // Re-apply once after layout settles to avoid ending above target.
        setTimeout(function () {
          var refreshedTarget = document.getElementById(targetId);
          if (refreshedTarget) {
            refreshedTarget.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          }
        }, 220);

        return true;
      }

      // Let the click-driven server callback patch the DOM before scrolling.
      requestAnimationFrame(function () {
        setTimeout(function () {
          if (tryScrollWhenReady()) {
            cleanup();
            return;
          }

          // React to actual DOM insertions/updates instead of fixed retry counts.
          observer = new MutationObserver(function () {
            if (tryScrollWhenReady()) {
              cleanup();
              return;
            }

            if (Date.now() - startAt > maxWaitMs) {
              cleanup();
            }
          });

          if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
          }

          // Safety net to avoid leaving observers alive indefinitely.
          fallbackTimer = setTimeout(cleanup, maxWaitMs + 100);
        }, 0);
      });

      return "";
    },

    show_text_field: function () {
      document.getElementById("manual-field").classList.remove("hidden");
      document.getElementById("drop-container").classList.add("hidden");
      document.getElementById("manual-insert").classList.add("hidden");
    },
  },
});

// Tree zoom controls event handler using event delegation
document.addEventListener("click", function (e) {
  var target = e.target;

  // Check if clicked element is a zoom button
  if (!target.classList.contains("tree-zoom-btn")) return;

  var cytoId = target.getAttribute("data-cyto-id");
  if (!cytoId) return;

  // Find the cytoscape element
  var cytoEl = document.getElementById(cytoId);
  if (!cytoEl || !cytoEl._cyreg || !cytoEl._cyreg.cy) return;

  var cy = cytoEl._cyreg.cy;
  var currentZoom = cy.zoom();
  var zoomFactor = 1.3;
  var newZoom;

  if (target.classList.contains("tree-zoom-in")) {
    // Zoom in
    newZoom = Math.min(currentZoom * zoomFactor, cy.maxZoom());
    cy.zoom({
      level: newZoom,
      renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
    });
  } else if (target.classList.contains("tree-zoom-out")) {
    // Zoom out
    newZoom = Math.max(currentZoom / zoomFactor, cy.minZoom());
    cy.zoom({
      level: newZoom,
      renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
    });
  } else if (target.classList.contains("tree-zoom-reset")) {
    // Reset zoom and pan to fit
    cy.fit(undefined, 20);
  }
});

// Download trigger buttons - click the hidden placeholder buttons
document.addEventListener("click", function (e) {
  var target = e.target.closest(".download-climatic-trigger");
  if (target) {
    var hiddenBtn = document.getElementById("download-btn-climatic");
    if (hiddenBtn) hiddenBtn.click();
    return;
  }

  target = e.target.closest(".download-genetic-trigger");
  if (target) {
    var hiddenBtn = document.getElementById("download-btn-genetic");
    if (hiddenBtn) hiddenBtn.click();
    return;
  }
});
