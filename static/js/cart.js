document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all Add to Cart buttons
    document.querySelectorAll('.js-add-cart').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const productId = this.getAttribute('data-product-id');
            
            // Find the closest quantity input
            let quantity = 1; // Default quantity
            const productContainer = this.closest('.product-single__addtocart, .pc__img-wrapper');
            if (productContainer) {
                const quantityInput = productContainer.querySelector('.qty-control__number');
                if (quantityInput) {
                    quantity = parseInt(quantityInput.value) || 1;
                }
            }
            
            // Debug logs
            console.log('Adding to cart:', {
                productId: productId,
                quantity: quantity
            });

            // Make AJAX call to add to cart
            fetch('/add-to-cart/', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity
                })
            })
            .then(response => {
                if (response.status === 401) {
                    window.location.href = '/login/?next=' + window.location.pathname;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (data) {
                    console.log('Success:', data);
                    
                    // Update cart count in header
                    updateCartCount(data.cart_items_count);
                    
                    // Update cart drawer content
                    updateCartDrawer(data.cart_items);
                    
                    // Show success message
                    showNotification('Product added to cart successfully!');
                    
                    // Open cart drawer
                    openCartDrawer();
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                showNotification('Error adding product to cart. Please try again.', 'error');
            });
        });
    });

    // Add quantity control functionality
    document.querySelectorAll('.qty-control').forEach(control => {
        const input = control.querySelector('.qty-control__number');
        const reduceBtn = control.querySelector('.qty-control__reduce');
        const increaseBtn = control.querySelector('.qty-control__increase');

        if (input && reduceBtn && increaseBtn) {
            // Flag to prevent multiple updates
            let isUpdating = false;

            // Reduce quantity
            reduceBtn.addEventListener('click', () => {
                if (isUpdating) return; // Prevent multiple clicks
                isUpdating = true; // Set flag

                let value = parseInt(input.value) || 1;
                console.log('Reduce button clicked. Current value:', value); // Debug log
                if (value > 1) {
                    input.value = value - 1;
                }

                isUpdating = false; // Reset flag
            });

            // Increase quantity
            increaseBtn.addEventListener('click', () => {
                if (isUpdating) return; // Prevent multiple clicks
                isUpdating = true; // Set flag

                let value = parseInt(input.value) || 1;
                console.log('Increase button clicked. Current value:', value); // Debug log
                const max = input.getAttribute('max');
                if (!max || value < parseInt(max)) {
                    input.value = value + 1;
                }

                isUpdating = false; // Reset flag
            });

            // Validate manual input
            input.addEventListener('change', () => {
                let value = parseInt(input.value) || 1;
                const max = input.getAttribute('max');
                if (value < 1) {
                    input.value = 1;
                } else if (max && value > parseInt(max)) {
                    input.value = max;
                }
            });
        }
    });



    // Helper function to update cart count
    function updateCartCount(count) {
        const cartCountElements = document.querySelectorAll('.js-cart-items-count');
        cartCountElements.forEach(element => {
            element.textContent = count;
        });
    }

    // Helper function to update cart drawer
    function updateCartDrawer(cartItems) {
        const cartDrawer = document.querySelector('.cart-drawer-items-list');
        if (!cartDrawer) return;

        if (!cartItems || cartItems.length === 0) {
            cartDrawer.innerHTML = `
                <div class="text-center py-4">
                    <p>Your cart is empty</p>
                </div>
            `;
            return;
        }

        let html = '';
        cartItems.forEach((item, index) => {
            html += `
                <div class="cart-drawer-item d-flex position-relative">
                    <div class="position-relative">
                        <a href="/product/${item.product.id}">
                            <img loading="lazy" class="cart-drawer-item__img" 
                                 src="${item.product.image.url}" 
                                 alt="${item.product.name}">
                        </a>
                    </div>
                    <div class="cart-drawer-item__info flex-grow-1">
                        <h6 class="cart-drawer-item__title fw-normal">
                            <a href="/product/${item.product.id}">${item.product.name}</a>
                        </h6>
                        ${item.color ? `<p class="cart-drawer-item__option text-secondary">Color: ${item.color}</p>` : ''}
                        ${item.size ? `<p class="cart-drawer-item__option text-secondary">Size: ${item.size}</p>` : ''}
                        <div class="d-flex align-items-center justify-content-between mt-1">
                            <div class="qty-control position-relative">
                                <input type="number" name="quantity" value="${item.quantity}" min="1" 
                                       class="qty-control__number border-0 text-center"
                                       data-product-id="${item.product.id}">
                                <div class="qty-control__reduce text-start">-</div>
                                <div class="qty-control__increase text-end">+</div>
                            </div>
                            <span class="cart-drawer-item__price money price">$${item.get_total_price}</span>
                        </div>
                    </div>
                    <button class="btn-close-xs position-absolute top-0 end-0 js-cart-item-remove" 
                            data-product-id="${item.product.id}"></button>
                </div>
                ${index < cartItems.length - 1 ? '<hr class="cart-drawer-divider">' : ''}
            `;
        });
        cartDrawer.innerHTML = html;

        // Update cart subtotal
        const subtotalElement = document.querySelector('.js-cart-subtotal');
        if (subtotalElement) {
            const total = cartItems.reduce((sum, item) => sum + parseFloat(item.get_total_price), 0);
            subtotalElement.textContent = total.toFixed(2);
        }
    }

    // Helper function to open cart drawer
    function openCartDrawer() {
        const cartDrawer = document.getElementById('cartDrawer');
        if (cartDrawer) {
            cartDrawer.classList.add('aside_active');
            document.body.classList.add('overflow-hidden');
        }
    }

    // Helper function to show notifications
    function showNotification(message, type = 'success') {
        // You can implement your preferred notification system here
        alert(message);
    }

    // Helper function to get CSRF token
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
});