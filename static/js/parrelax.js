
document.addEventListener("DOMContentLoaded", () => {
  const dynamicImage = document.getElementById("dynamicImage");
  const greyBackground = document.getElementById("greyBackground");
  const revealText = document.getElementById("revealText");
  const parallaxText = document.getElementById("parallaxText");

  gsap.registerPlugin(ScrollTrigger);

  // Animate the image scaling from 100px to cover the screen
  gsap.to(dynamicImage, {
    width: "100vw",
    height: "100vh",
    borderRadius: "0px",
    opacity: 1,
    ease: "power4.out",
    scrollTrigger: {
      trigger: dynamicImage,
      start: "top center",
      end: "bottom top",
      scrub: 0.5,
    }
  });

  // Make the grey background appear as the image enlarges
  gsap.to(greyBackground, {
    opacity: 1,
    ease: "power2.inOut",
    scrollTrigger: {
      trigger: dynamicImage,
      start: "center center",
      end: "bottom top",
      scrub: 0.5,
    }
  });

  // Fade out the image as the grey background appears
  gsap.to(dynamicImage, {
    opacity: 0,
    ease: "power2.inOut",
    scrollTrigger: {
      trigger: dynamicImage,
      start: "center center",
      end: "bottom top",
      scrub: 0.5,
    }
  });

  // Reveal the main text when the image is fully enlarged
  gsap.to(revealText, {
    opacity: 0,
    ease: "power4.out",
    scrollTrigger: {
      trigger: dynamicImage,
      start: "bottom top",
      end: "bottom bottom",
      scrub: 0.5,
    }
  });

  // Parallax effect on text
  gsap.to(parallaxText, {
    y: "200px", // Parallax movement
    opacity: 0,
    ease: "back.inOut", // Smooth easing
    scrollTrigger: {
      trigger: dynamicImage,
      start: "top top",
      end: "bottom bottom",
      scrub: 5, // Slower and smoother scrolling
    }
  });
});
