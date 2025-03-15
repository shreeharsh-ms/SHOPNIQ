// static/js/buynow.js

function buyNow(productId, button) {
    const quantityInput = document.querySelector(`input[name="quantity"][data-product-id="${productId}"]`);
    const quantity = quantityInput ? quantityInput.value || 1 : 1;

    // Button animation (Loader)
    const btnText = button.querySelector(".btn-text");
    const loader = button.querySelector(".loader");
    const checkmark = button.querySelector(".checkmark");

    btnText.style.display = "none";
    loader.style.display = "inline-block";

    // Send AJAX request (Using fetch API)
    fetch("/buy-now/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken') // Ensure CSRF token is sent
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: parseInt(quantity, 10),
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            // Success: Redirect to checkout
            loader.style.display = "none";
            checkmark.style.display = "inline-block";
            setTimeout(() => {
                window.location.href = data.redirect_url;
            }, 1500);
        } else {
            // Error: Reset and alert user
            alert(data.message || "Something went wrong!");
            resetButton(button);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Network error. Try again!");
        resetButton(button);
    });
}

// Helper: Reset Button State
function resetButton(button) {
    const btnText = button.querySelector(".btn-text");
    const loader = button.querySelector(".loader");
    const checkmark = button.querySelector(".checkmark");

    btnText.style.display = "inline-block";
    loader.style.display = "none";
    checkmark.style.display = "none";
}

// Helper: Get CSRF Token from Cookies
function getCSRFToken() {
    return document.cookie.split('; ').find(row => row.startsWith('csrftoken='))
           ?.split('=')[1];
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}