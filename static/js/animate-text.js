
document.addEventListener("DOMContentLoaded", function () {
    // Select all elements with the class `animate-text`
    const textElements = document.querySelectorAll('.animate-text');
  
    textElements.forEach((element) => {
      // Split the text into lines, words, and characters
      let typeSplit = new SplitType(element, {
        types: 'lines, words, chars',
        tagName: 'span' // Wrap split parts in `span`
      });
  
      // Apply the GSAP animation to the `.word` elements
      gsap.from(element.querySelectorAll('.word'), {
        y: '100%', // Slide in from below
        opacity: 0, // Start with zero opacity
        duration: 4, // Animation duration
        ease: 'power4.out', // Smooth easing
        stagger: 0.1, // Delay between each word
  
        scrollTrigger: {
          trigger: element, // Trigger animation when this element enters the viewport
          start: '100% 100%', // Element's middle reaches the center of the viewport
          end: '100% 100%', // End point ensures it's triggered only when fully centered
          toggleActions: 'play none none none', // Trigger only once
        },
      });
    });
  });
  