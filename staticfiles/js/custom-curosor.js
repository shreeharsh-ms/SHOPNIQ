document.addEventListener("DOMContentLoaded", function () {
  const cursor = document.querySelector(".custom-cursor");
  const circleText = document.querySelector("textPath");
  const cursorENABLEElements = document.querySelectorAll(".cursorENABLE");

  // Track mouse movement and update cursor position
  document.addEventListener("mousemove", (e) => {
    const x = e.clientX;
    const y = e.clientY;

    // Update the custom cursor position, aligning its center with the pointer
    cursor.style.transform = `translate(${x}px, ${y}px)`;
  });

  // Show the custom cursor and hide the default cursor when entering a .cursorENABLE element
  cursorENABLEElements.forEach((element) => {
    element.addEventListener("mouseenter", () => {
      cursor.style.display = "block"; // Show the custom cursor
      document.body.style.cursor = "none"; // Hide the default cursor
    });
    element.addEventListener("mouseleave", () => {
      cursor.style.display = "none"; // Hide the custom cursor
      document.body.style.cursor = "auto"; // Restore the default cursor
    });
  });

  // Animate circular text rotation
  let rotation = 0;
  const textPathLength = 19; // Total text length around the circle
  setInterval(() => {
    rotation += 1;
    circleText.setAttribute("startOffset", `${rotation % textPathLength}`);
  }, 20);

  // Add hover effect for clickable elements inside the .cursorENABLE class
  const clickableElements = document.querySelectorAll(".cursorENABLE button, .cursorENABLE a, .cursorENABLE .content h1");
  clickableElements.forEach((el) => {
    el.addEventListener("mouseenter", () => {
      cursor.classList.add("hover");
    });
    el.addEventListener("mouseleave", () => {
      cursor.classList.remove("hover");
    });
  });
});
