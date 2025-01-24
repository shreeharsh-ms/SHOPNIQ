document.addEventListener("DOMContentLoaded", () => {
  const appRoot = document.getElementById("page");
  const root = document.documentElement;

  // Generalized function to handle page transitions
  const startTransition = (route) => {
      const loader = document.querySelector(".loader");
      const loaderText = document.querySelector(".loader-text");

      // Show loader and set the loading message
      loader.style.transform = "translateX(0%)";
      loaderText.textContent = `Loading ${route} page...`;

      // Apply SplitType to animate the loader text
      let typeSplit = new SplitType(loaderText, { types: 'lines, words, chars', tagName: 'span' });

      // GSAP animation for the loader text
      gsap.from(loaderText.querySelectorAll('.char'), {
          opacity: 0,
          duration: 0.35,
          ease: 'power1.out',
          stagger: 0.05,
      });

      // Wait for the loader animation to play, then switch the route
      setTimeout(() => {
          appRoot.dataset.route = route;

          // Hide the loader after route change
          setTimeout(() => {
              loader.style.transform = "translateX(100%)";
              root.classList.remove("disable-hover");

              // Hide the loader after the animation ends
              setTimeout(() => {
                  loader.style.display = "none"; // Hide the loader after transition
              }, 500); // Wait until the animation ends
          }, 500); // Delay for loader to stay visible briefly after route update
      }, 1000); // Simulated loading delay
  };

  // Initial loader setup when the page loads
  window.addEventListener("load", () => {
      const loader = document.querySelector(".loader");
      const loaderText = document.querySelector(".loader-text");

      // Dynamically fetch the page title and use it as the loading message
      const pageTitle = document.title;
      loaderText.textContent = `${pageTitle}...`;
      loader.style.transform = "translateX(0%)";

      // Apply SplitType to animate the loader text
      let typeSplit = new SplitType(loaderText, { types: 'lines, words, chars', tagName: 'span' });

      // GSAP animation for the loader text
      gsap.from(loaderText.querySelectorAll('.char'), {
          opacity: 0,
          duration: 0.35,
          ease: 'power1.out',
          stagger: 0.05,
      });

      // Hide the loader after a short delay
      setTimeout(() => {
          loader.style.transform = "translateX(100%)";
          appRoot.dataset.route = "a";

          // Hide the loader after the animation ends
          setTimeout(() => {
              loader.style.display = "none"; // Hide the loader after transition
          }, 500); // Wait until the animation ends
      }, 1000); // Initial loading delay
  });
});
