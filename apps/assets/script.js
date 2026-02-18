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
          navbar_function: function() {
            responsiveNavbar();
            
            // Wait for CSS transition to complete before resizing charts (avoid lags)
            const navbar = document.getElementById('nav-bar');
            if (navbar) {
                let handled = false;
                function handleTransitionEnd(e) {
                    if (e.propertyName === 'width' && !handled) {
                        handled = true;
                        navbar.removeEventListener('transitionend', handleTransitionEnd);
                        requestAnimationFrame(function() {
                            window.dispatchEvent(new Event('resize'));
                        });
                    }
                }
                navbar.addEventListener('transitionend', handleTransitionEnd);
                setTimeout(function() {
                    if (!handled) {
                        handled = true;
                        navbar.removeEventListener('transitionend', handleTransitionEnd);
                        window.dispatchEvent(new Event('resize'));
                    }
                }, 500);
            }
            
            return '';
          },

          share_result_function: function() {
            navigator.clipboard.writeText(window.location.href);
            document.getElementById('share_tooltip').classList.add("visible");
            window.setTimeout(function() {
                document.getElementById('share_tooltip').classList.remove("visible");
            }, 4000);
            return ''
          },

          collapse_result_section_function: function(trigger, collapse_section, trigger_id) {
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

          next_option_function: function(currentDiv, desireDiv) {
            document.getElementById(desireDiv).scrollIntoView({ behavior: 'smooth', block: 'start'});
            return ''
          },

          show_text_field: function () {
            document.getElementById('manual-field').classList.remove("hidden");
            document.getElementById('drop-container').classList.add("hidden");
            document.getElementById('manual-insert').classList.add("hidden");
          }
      }
    });