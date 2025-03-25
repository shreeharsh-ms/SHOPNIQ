document.addEventListener("DOMContentLoaded", function () {
    const applyCouponBtn = document.getElementById("applyCouponBtn");
    const couponInput = document.getElementById("coupon_code");
    const couponMessage = document.getElementById("couponMessage");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    applyCouponBtn.addEventListener("click", function () {
        const couponCode = couponInput.value.trim();
        couponMessage.textContent = "";

        // Validate coupon code
        if (!couponCode) {
            couponMessage.textContent = "Please enter a coupon code.";
            couponMessage.style.color = "red";
            return;
        }

        // Send coupon request to backend
        fetch("/apply-coupon/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
            },
            body: JSON.stringify({ coupon_code: couponCode }),
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Success message
                    couponMessage.style.color = "green";
                    couponMessage.textContent = data.message || `Coupon applied: ${data.discount_percentage} discount!`;

                    // Update checkout totals dynamically
                    updateCheckoutTotals(data);
                } else {
                    // Error message
                    couponMessage.style.color = "red";
                    couponMessage.textContent = data.message || "Invalid coupon code.";
                }
            })
            .catch(error => {
                console.error("Error applying coupon:", error);
                couponMessage.style.color = "red";
                couponMessage.textContent = "An error occurred. Please try again.";
            });
    });

    // Helper function to update checkout totals
    function updateCheckoutTotals(data) {
        const checkoutTotals = document.querySelector(".checkout-totals");
        checkoutTotals.innerHTML = `
            <!-- Subtotal -->
            <tr>
                <th>SUBTOTAL</th>
                <td>
                    $${data.total_amount.toFixed(2)}
                    ${data.discount_amount > 0 ? `<span style="color: green;">
                        (Coupon Applied: -$${data.discount_amount.toFixed(2)} | ${data.discount_percentage})
                    </span>` : ""}
                </td>
            </tr>

            <!-- Shipping -->
            <tr>
                <th>SHIPPING</th>
                <td>${data.shipping === 0 ? "Free shipping" : `$${data.shipping.toFixed(2)}`}</td>
            </tr>

            <!-- GST (18%) -->
            <tr>
                <th>GST (18%)</th>
                <td>$${data.gst.toFixed(2)}</td>
            </tr>

            <!-- Total -->
            <tr>
                <th>TOTAL</th>
                <td>$${data.grand_total.toFixed(2)}</td>
            </tr>

            <!-- Applied Coupon Info -->
            <tr>
                <th>Applied Coupon</th>
                <td><strong>${data.applied_coupon || "N/A"}</strong> - Saved $${data.discount_amount.toFixed(2)}</td>
            </tr>
        `;
    }
});
