

    // Scroll detection to minimize navBar

    //let prevScroll = window.scrollY;
    let open = true;
    // window.onscroll = ()  => {
    //   responsiveNavbar()
    // };

    function responsiveNavbar() {
      if (open) {
          console.log('plus petit');
          document.getElementById('lab-container').classList.add("minimized");
          document.getElementById('navBar').classList.add("minimized");
          document.getElementById('lab-name').classList.add("minimized");
          document.getElementById('theme-switch').classList.add("minimized");
          document.getElementById('nav-link').classList.add("minimized");
          document.getElementById('gitHub-container').classList.add("minimized");

          open = false;
          // prevScroll = window.scrollY;
          // localStorage.setItem('scroll', prevScroll)

        }

        else {
          console.log('plus grand');
          document.getElementById('lab-container').classList.remove("minimized");
          document.getElementById('navBar').classList.remove("minimized");
          document.getElementById('lab-name').classList.remove("minimized");
          document.getElementById('theme-switch').classList.remove("minimized");
          document.getElementById('nav-link').classList.remove("minimized");
          document.getElementById('gitHub-container').classList.remove("minimized");

          open = true
          // prevScroll = window.scrollY;
          // localStorage.setItem('scroll', prevScroll)

        }
    }

    window.dash_clientside = Object.assign({}, window.dash_clientside, {
      clientside: {
          navbar_function: function() {
            responsiveNavbar()
            return ''
          }
      }
    });