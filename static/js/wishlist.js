// Wishlist toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all wishlist icons
    document.querySelectorAll('.js-add-wishlist').forEach(icon => {
      icon.addEventListener('click', function(e) {
        e.preventDefault();
        const productId = this.getAttribute('data-product-id');
        toggleWishlistItem(productId, this);
      });
    });
    
    // Add click event listeners for product detail page wishlist
    const detailWishlistBtn = document.querySelector('.add-to-wishlist');
    if (detailWishlistBtn) {
      detailWishlistBtn.addEventListener('click', function(e) {
        e.preventDefault();
        // Fix: Get product ID from onclick attribute if data-product-id is not available
        const productId = this.getAttribute('data-product-id') || this.getAttribute('onclick').match(/'([^']+)'/)[1];
        console.log("Product ID for wishlist:", productId); // Debug log
        toggleWishlist(productId, this);
      });
    }
  });
  
  function toggleWishlistItem(productId, icon) {
    // Check if the item is already in the wishlist (has active class)
    const isInWishlist = icon.classList.contains('active');
    
    // Validate product ID
    if (!productId) {
      console.error("Product ID is missing");
      return;
    }
    
    // Determine the endpoint based on whether we're adding or removing
    const endpoint = isInWishlist 
      ? `/api/wishlist/remove/${productId}/` 
      : '/api/wishlist/add/';
    
    // Determine the method based on the action
    const method = isInWishlist ? 'DELETE' : 'POST';
    
    // Prepare the request body for POST requests
    const body = method === 'POST' 
      ? JSON.stringify({ product_id: productId }) 
      : null;
    
    fetch(endpoint, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: body,
      credentials: 'same-origin'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      if ((method === 'POST' && data.success) || (method === 'DELETE' && data.success)) {
        // Toggle the active class
        icon.classList.toggle('active');
        
        // Optional: Show success message
        const message = isInWishlist 
          ? 'Product removed from wishlist!' 
          : 'Product added to wishlist!';
        
        // You can use a toast notification or other UI feedback here
        console.log(message);
      } else {
        console.error(data.message || 'Operation failed');
      }
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  
  // Function for product detail page wishlist toggle
  function toggleWishlist(productId, element) {
    // Validate product ID
    if (!productId) {
      console.error("Product ID is missing");
      return;
    }
    
    // Determine if the product is already in the wishlist
    const heartIcon = element.querySelector('svg use') || element.querySelector('.wishlist-icon');
    const isInWishlist = heartIcon.style.fill === 'red' || (heartIcon.classList && heartIcon.classList.contains('active'));
    const wishlistText = element.querySelector('.wishlist-text');
    
    // Set the endpoint based on whether we're adding or removing
    const endpoint = isInWishlist 
      ? `/api/wishlist/remove/${productId}/` 
      : '/api/wishlist/add/';
    
    // Set the method based on the action
    const method = isInWishlist ? 'DELETE' : 'POST';
    
    // Prepare the request body for POST requests
    const body = method === 'POST' 
      ? JSON.stringify({ product_id: productId }) 
      : null;
    
    // Show loading state
    element.style.opacity = '0.7';
    
    fetch(endpoint, {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: body,
      credentials: 'same-origin'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Reset loading state
      element.style.opacity = '1';
      
      if ((method === 'POST' && data.success) || (method === 'DELETE' && data.success)) {
        // Toggle the fill style for SVG
        if (heartIcon.tagName.toLowerCase() === 'use') {
          heartIcon.style.fill = isInWishlist ? 'none' : 'red';
        } 
        else {
          // Toggle the active class if it's not an SVG use element
          heartIcon.classList.toggle('active');
          heartIcon.style.fill = isInWishlist ? 'none' : 'red';
        }
        
        // Update text if it exists
        if (wishlistText) {
          wishlistText.textContent = isInWishlist ? 'Add to Wishlist' : 'Remove from Wishlist';
        }
        
        // Optional: Show success message
        const message = isInWishlist 
          ? 'Product removed from wishlist!' 
          : 'Product added to wishlist!';
        
        // You can add a toast notification here
        console.log(message);
      } else {
        console.error(data.message || 'Operation failed');
      }
    })
    .catch(error => {
      // Reset loading state
      element.style.opacity = '1';
      console.error('Error:', error);
    });
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