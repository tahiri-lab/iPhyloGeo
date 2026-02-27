// Direct DOM-based nav highlight for instant feedback
function updateNavHighlight() {
  var pathname = window.location.pathname;
  var linkMap = {
    '/': 'nav-link-home',
    '/getStarted': 'nav-link-getstarted',
    '/results': 'nav-link-results',
    '/settings': 'nav-link-settings',
    '/help': 'nav-link-help'
  };
  var navIds = ['nav-link-home', 'nav-link-getstarted', 'nav-link-results'];
  var bottomIds = ['nav-link-settings', 'nav-link-help'];
  var activeId = linkMap[pathname] || '';

  navIds.forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.className = (id === activeId) ? 'nav-link selected' : 'nav-link';
  });
  bottomIds.forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.className = (id === activeId) ? 'bottom-nav-item selected' : 'bottom-nav-item';
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
window.addEventListener('popstate', function () {
  setTimeout(updateNavHighlight, 0);
});

// Re-apply highlight whenever Dash overwrites our classes via its VDOM
(function () {
  var _updating = false;
  var ids = ['nav-link-home', 'nav-link-getstarted', 'nav-link-results', 'nav-link-settings', 'nav-link-help'];

  var observer = new MutationObserver(function () {
    if (_updating) return;
    _updating = true;
    updateNavHighlight();
    _updating = false;
  });

  function startObserving() {
    ids.forEach(function (id) {
      var el = document.getElementById(id);
      if (el) observer.observe(el, { attributes: true, attributeFilter: ['class'] });
    });
  }

  // Patch updateNavHighlight to disconnect/reconnect observer around updates
  var origUpdate = updateNavHighlight;
  updateNavHighlight = function () {
    observer.disconnect();
    origUpdate();
    startObserving();
  };

  document.addEventListener('DOMContentLoaded', function () {
    startObserving();
    updateNavHighlight();
  });
})();

let open = true;

function responsiveNavbar() {
  const labContainer = document.getElementById('lab-container');
  const navBar = document.getElementById('nav-bar');
  const labName = document.getElementById('lab-name');
  const themeSwitch = document.getElementById('theme-switch');
  const navLink = document.getElementById('nav-link');
  const gitHubContainer = document.getElementById('gitHub-container');

  if (open) {
    if (labContainer) labContainer.classList.add("minimized");
    if (navBar) navBar.classList.add("minimized");
    if (labName) labName.classList.add("minimized");
    if (themeSwitch) themeSwitch.classList.add("minimized");
    if (navLink) navLink.classList.add("minimized");
    if (gitHubContainer) gitHubContainer.classList.add("minimized");

    open = false;
  }

  else {
    if (labContainer) labContainer.classList.remove("minimized");
    if (navBar) navBar.classList.remove("minimized");
    if (labName) labName.classList.remove("minimized");
    if (themeSwitch) themeSwitch.classList.remove("minimized");
    if (navLink) navLink.classList.remove("minimized");
    if (gitHubContainer) gitHubContainer.classList.remove("minimized");

    open = true
  }
}

window.dash_clientside = Object.assign({}, window.dash_clientside, {
  clientside: {
    navbar_function: function () {
      responsiveNavbar();

      // Wait for CSS transition to complete before resizing charts (avoid lags)
      const navbar = document.getElementById('nav-bar');
      if (navbar) {
        let handled = false;
        function handleTransitionEnd(e) {
          if (e.propertyName === 'width' && !handled) {
            handled = true;
            navbar.removeEventListener('transitionend', handleTransitionEnd);
            requestAnimationFrame(function () {
              window.dispatchEvent(new Event('resize'));
            });
          }
        }
        navbar.addEventListener('transitionend', handleTransitionEnd);
        setTimeout(function () {
          if (!handled) {
            handled = true;
            navbar.removeEventListener('transitionend', handleTransitionEnd);
            window.dispatchEvent(new Event('resize'));
          }
        }, 500);
      }

      return '';
    },

    update_nav_selected: function (pathname) {
      var sel = {
        '/': 0,
        '/getStarted': 1,
        '/results': 2,
        '/settings': 3,
        '/help': 4
      };
      var idx = sel[pathname];
      if (idx === undefined) idx = -1;
      return [
        idx === 0 ? 'nav-link selected' : 'nav-link',
        idx === 1 ? 'nav-link selected' : 'nav-link',
        idx === 2 ? 'nav-link selected' : 'nav-link',
        idx === 3 ? 'bottom-nav-item selected' : 'bottom-nav-item',
        idx === 4 ? 'bottom-nav-item selected' : 'bottom-nav-item'
      ];
    },

    share_result_function: function () {
      navigator.clipboard.writeText(window.location.href);
      document.getElementById('share_tooltip').classList.add("visible");
      window.setTimeout(function () {
        document.getElementById('share_tooltip').classList.remove("visible");
      }, 4000);
      return ''
    },

    collapse_result_section_function: function (trigger, collapse_section, trigger_id) {
      if (trigger >= 1) {
        if (document.getElementById(collapse_section).classList.contains("collapse-row")) {
          document.getElementById(trigger_id).classList.remove("close");
          document.getElementById(collapse_section).classList.remove("collapse-row");
        } else {
          document.getElementById(trigger_id).classList.add("close");
          document.getElementById(collapse_section).classList.add("collapse-row");
        }
      }
      return ''
    },

    next_option_function: function (currentDiv, desireDiv) {
      document.getElementById(desireDiv).scrollIntoView({ behavior: 'smooth', block: 'start' });
      return ''
    },

    show_text_field: function () {
      document.getElementById('manual-field').classList.remove("hidden");
      document.getElementById('drop-container').classList.add("hidden");
      document.getElementById('manual-insert').classList.add("hidden");
    }
  }
});