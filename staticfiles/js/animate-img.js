document.addEventListener("DOMContentLoaded", function () {
    // Ensure GSAP and ScrollTrigger are available
    if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
      console.error("GSAP or ScrollTrigger is not loaded.");
      return;
    }
  
    gsap.registerPlugin(ScrollTrigger);
  
    // Function to create reveal animations
    function createRevealAnimation(selector) {
      const elements = document.querySelectorAll(selector); // Select elements by ID, class, or tag
  
      if (!elements.length) {
        console.warn(`No elements found for selector: ${selector}`);
        return;
      }
  
      elements.forEach((element) => {
        // Check if the element has an image
        const image = element.querySelector("img");
  
        const tl = gsap.timeline({
          scrollTrigger: {
            trigger: element,
            start: "top 80%", // Trigger animation when element enters viewport
            end: "bottom 30%", // End trigger
            toggleActions: "play reverse play reset", // Reverse animation when scrolling out of viewport
            onReverseComplete: () => {
              // Add this callback to reset the animation with desired speed and easing
              tl.timeScale(1).reverse();  // Reset speed for reverse with easing
            }
          },
        });
  
        // Reveal animation for the container
        tl.set(element, { autoAlpha: 1 }); // Ensure the element is visible
        tl.from(element, {
          duration: 1.5,
          xPercent: -100,
          delay: -1.5,
          ease: "power2.out", // Smooth easing for revealing
        });
  
        // If an image is present, add its animation
        if (image) {
          tl.from(image, {
            duration: 1.5,
            xPercent: 100,
            scale: 1.3,
            delay: -1.5,
            ease: "power2.out", // Smooth easing for image reveal
          });
        } else {
          console.warn(`No image found inside element:`, element);
        }
      });
    }
  
    // Function to manually trigger animations via the console
    window.triggerAnimation = function (selector) {
      const elements = document.querySelectorAll(selector); // Select elements by ID, class, or tag
  
      if (!elements.length) {
        console.warn(`No elements found for selector: ${selector}`);
        return;
      }
  
      elements.forEach((element) => {
        // Check if the element has an image
        const image = element.querySelector("img");
  
        const tl = gsap.timeline();
        tl.set(element, { autoAlpha: 1 }); // Ensure the element is visible
        tl.from(element, {
          duration:0.7,
          xPercent: -100,
          ease: "expo.out", // Smooth easing for revealing
        });
  
        // If an image is present, add its animation
        if (image) {
          tl.from(image, {
            duration: 0.7,
            xPercent: 100,
            scale: 1.3,
            delay: -0.5,
            ease: "expo.out", // Smooth easing for image reveal
          });
        } else {
          console.warn(`No image found inside element:`, element);
        }
      });
  
      console.log(`Animation triggered for selector: ${selector}`);
    };
  
    // Automatically apply animations to elements with the "reveal" class
    createRevealAnimation(".reveal");
  
    console.log("Use triggerAnimation(selector) to manually run animations.");
  
  
  });
  