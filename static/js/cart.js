document.addEventListener('DOMContentLoaded', function () {
    console.log("🛒 Cart System Initialized");

    // Attach event listeners
    attachAddToCartListeners();
    attachQuantityListeners();
    attachRemoveListeners();
});

// Get CSRF Token
function getCSRFToken() {
    return document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
}

// 🟢 Add to Cart
function attachAddToCartListeners() {
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('js-add-cart')) {
            e.preventDefault();
            const productId = e.target.getAttribute('data-product-id');
            const quantityInput = e.target.closest('.product-single__addtocart')
                ?.querySelector('.qty-control__number');
            const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;

            console.log(`🛒 Adding product: ${productId}, Quantity: ${quantity}`);

            fetch('/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ product_id: productId, quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Product added to cart');
                    updateCartCount(data.cart_items_count);
                    updateCartDrawer(data.cart_items);
                    openCartDrawer();
                } else {
                    alert(`❌ Error: ${data.error}`);
                }
            })
            .catch(err => console.error("❌ Failed to add to cart:", err));
        }
    });
}

// 🔢 Update Quantity
function attachQuantityListeners() {
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('qty-control__reduce') || e.target.classList.contains('qty-control__increase')) {
            const control = e.target.closest('.qty-control');
            const input = control.querySelector('.qty-control__number');
            const productId = input.dataset.productId;
            let newQuantity = parseInt(input.value) || 1;

            if (e.target.classList.contains('qty-control__reduce')) {
                newQuantity = Math.max(1, newQuantity - 1);
            } else if (e.target.classList.contains('qty-control__increase')) {
                newQuantity += 1;
            }

            input.value = newQuantity;
            updateCart(productId, newQuantity);
        }
    });

    // Handle manual input change
    document.body.addEventListener('change', (e) => {
        if (e.target.classList.contains('qty-control__number')) {
            const input = e.target;
            const productId = input.dataset.productId;
            const newQuantity = Math.max(1, parseInt(input.value) || 1);
            input.value = newQuantity;
            updateCart(productId, newQuantity);
        }
    });
}

// 🗑️ Remove from Cart
function attachRemoveListeners() {
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-cart')) {
            e.preventDefault();
            const productId = e.target.getAttribute('data-product-id');
            if (!confirm("🗑️ Remove this item?")) return;

            fetch(`/api/remove-from-cart/${productId}/`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': getCSRFToken() }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ Item removed');
                    updateCartCount(data.cart_items_count);
                    updateCartDrawer(data.cart_items);
                } else {
                    alert(`❌ Error: ${data.error}`);
                }
            })
            .catch(err => console.error("❌ Failed to remove item:", err));
        }
    });
}

// 📊 Update Cart Count
function updateCartCount(count) {
    document.querySelectorAll('.js-cart-items-count')
        .forEach(el => el.textContent = count);
}

// 🛍️ Update Cart Drawer
function updateCartDrawer(cartItems) {
    const cartDrawer = document.querySelector('.cart-drawer-items-list');
    if (!cartDrawer) return;

    if (!cartItems.length) {
        cartDrawer.innerHTML = "<p>Your cart is empty</p>";
        return;
    }

    cartDrawer.innerHTML = cartItems.map(item => `
        <div class="cart-item">
            <p>${item.product.name} x ${item.quantity}</p>
        </div>
    `).join('');
}

// 📦 Update Cart (Helper)
function updateCart(productId, quantity) {
    fetch('/update-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCount(data.cart_items_count);
            updateCartDrawer(data.cart_items);
        } else {
            alert(`❌ Error: ${data.error}`);
        }
    })
    .catch(err => console.error("❌ Update failed:", err));
}

// 📤 Open Cart Drawer
function openCartDrawer() {
    document.getElementById('cartDrawer')?.classList.add('aside_active');
    document.body.classList.add('overflow-hidden');
}
