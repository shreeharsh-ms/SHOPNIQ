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
                    ${data.discount_amount > 0 ? `
                        <span style="
                            display: inline-flex;
                            align-items: center;
                            background: #FFD700; /* Elegant gold tone for premium look */
                            color: #333; /* Dark grey for contrast */
                            padding: 4px 10px;
                            border-radius: 12px;
                            margin-left: 8px;
                            font-size: 0.85em;
                            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                            font-weight: 600;
                            letter-spacing: 0.5px;
                        ">
                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M8 12h8"></path>
                            </svg>
                            -$${data.discount_amount.toFixed(2)} (${data.discount_percentage}% OFF)
                        </span>
                    ` : ""}
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
    <td>
        ${data.applied_coupon ? `
            <div style="
                display: inline-flex;
                align-items: center;
                background: linear-gradient(135deg, #FFD700, #FFA500); /* Gold to Orange gradient */
                color: #333; /* Dark text for better readability */
                padding: 6px 12px;
                border-radius: 12px;
                font-size: 0.9em;
                font-weight: 600;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            ">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                    <path d="M21 6h-3V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v2H3a1 1 0 0 0-1 1v4a3 3 0 0 1 0 6v4a1 1 0 0 0 1 1h18a1 1 0 0 0 1-1v-4a3 3 0 0 1 0-6V7a1 1 0 0 0-1-1z"></path>
                    <path d="M7 9v1"></path>
                    <path d="M7 14v1"></path>
                </svg>
                ${data.applied_coupon}
            </div>
            <span style="
                color: #4CAF50; /* Soft green for positive savings */
                font-weight: 600;
                margin-left: 8px;
            ">
                - Saved $${data.discount_amount.toFixed(2)}
            </span>
        ` : `<strong style="color: #888;">N/A</strong>`}
    </td>
</tr>

        `;
    }
});
