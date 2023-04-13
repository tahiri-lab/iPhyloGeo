// Scroll detection to minimize navBar
    let open = false;
    window.onscroll = ()  => {
      open = true;
      responsiveNavbar()
    };

    function responsiveNavbar() {
      if (open) {
          document.getElementById('lab-container').classList.add("minimized");
          document.getElementById('nav-bar').classList.add("minimized");
          document.getElementById('lab-name').classList.add("minimized");
          document.getElementById('theme-switch').classList.add("minimized");
          document.getElementById('nav-link').classList.add("minimized");
          document.getElementById('gitHub-container').classList.add("minimized");

          open = false;
        }

        else {
          document.getElementById('lab-container').classList.remove("minimized");
          document.getElementById('nav-bar').classList.remove("minimized");
          document.getElementById('lab-name').classList.remove("minimized");
          document.getElementById('theme-switch').classList.remove("minimized");
          document.getElementById('nav-link').classList.remove("minimized");
          document.getElementById('gitHub-container').classList.remove("minimized");

          open = true
        }
    }

    window.dash_clientside = Object.assign({}, window.dash_clientside, {
      clientside: {
          navbar_function: function() {
            responsiveNavbar()
            return ''
          },

          next_option_function: function(currentDiv, desireDiv) {
            document.getElementById(desireDiv).scrollIntoView({ behavior: 'smooth', block: 'start'});
            return ''
          },

          show_text_field: function () {
            document.getElementById('manualField').classList.remove("hidden");
            document.getElementById('dropContainer').classList.add("hidden");
            document.getElementById('manualInsert').classList.add("hidden");
          }
      }
    });