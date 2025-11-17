// static/js/main.js - FIXED VERSION

// Main JavaScript for SomaliShop E-commerce

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    initializeMobileMenu();
    initializeCartFunctionality();
    initializeSearchFunctionality();
    initializeFormValidations();
    initializeImageLazyLoading();
    initializeSmoothScrolling();
    initializeToastNotifications();
    initializeWhatsAppLinks();
}

// Mobile Menu Functionality
function initializeMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const adminMobileMenuBtn = document.getElementById('adminMobileMenuBtn');
    const adminMobileMenu = document.getElementById('adminMobileMenu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }

    if (adminMobileMenuBtn && adminMobileMenu) {
        adminMobileMenuBtn.addEventListener('click', function() {
            adminMobileMenu.classList.toggle('hidden');
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu && !mobileMenu.contains(event.target) && mobileMenuBtn && !mobileMenuBtn.contains(event.target)) {
            mobileMenu.classList.add('hidden');
        }
        if (adminMobileMenu && !adminMobileMenu.contains(event.target) && adminMobileMenuBtn && !adminMobileMenuBtn.contains(event.target)) {
            adminMobileMenu.classList.add('hidden');
        }
    });
}

// WhatsApp Links - FIXED: Ensure all WhatsApp links open in new tab
function initializeWhatsAppLinks() {
    const whatsappLinks = document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp.com"], a[href*="api.whatsapp.com"]');
    whatsappLinks.forEach(link => {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
    });
}

// Cart Functionality
function initializeCartFunctionality() {
    updateCartCountDisplay();
    
    // Cart item quantity controls
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            const action = this.dataset.action;
            updateCartQuantity(productId, action);
        });
    });
}

function updateCartCountDisplay() {
    const cart = getCartFromStorage();
    const cartCountElements = document.querySelectorAll('.cart-count');
    
    cartCountElements.forEach(element => {
        if (cart.length > 0) {
            element.textContent = cart.reduce((total, item) => total + item.quantity, 0);
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    });
}

function getCartFromStorage() {
    try {
        return JSON.parse(localStorage.getItem('somaliShopCart')) || [];
    } catch (error) {
        console.error('Error reading cart from storage:', error);
        return [];
    }
}

function saveCartToStorage(cart) {
    try {
        localStorage.setItem('somaliShopCart', JSON.stringify(cart));
        updateCartCountDisplay();
    } catch (error) {
        console.error('Error saving cart to storage:', error);
    }
}

function updateCartQuantity(productId, action) {
    let cart = getCartFromStorage();
    const itemIndex = cart.findIndex(item => item.product_id === productId);
    
    if (itemIndex !== -1) {
        if (action === 'increase') {
            cart[itemIndex].quantity += 1;
        } else if (action === 'decrease') {
            cart[itemIndex].quantity -= 1;
            if (cart[itemIndex].quantity <= 0) {
                cart.splice(itemIndex, 1);
            }
        }
        
        saveCartToStorage(cart);
        showToast('Cart updated successfully', 'success');
        
        // Update cart page if we're on it
        if (window.location.pathname.includes('cart')) {
            setTimeout(() => {
                window.location.reload();
            }, 500);
        }
    }
}

// Search Functionality
function initializeSearchFunctionality() {
    const searchInput = document.querySelector('input[name="search"]');
    const searchForm = document.querySelector('form[method="GET"]');
    
    if (searchInput && searchForm) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2 || this.value.length === 0) {
                    searchForm.submit();
                }
            }, 500);
        });
    }
}

// Form Validations
function initializeFormValidations() {
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validatePhoneNumber(this);
        });
    });
}

function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        showInputError(input, 'Please enter a valid email address');
        return false;
    } else {
        clearInputError(input);
        return true;
    }
}

function validatePhoneNumber(input) {
    const phone = input.value;
    const phoneRegex = /^\+?[\d\s\-\(\)]{10,}$/;
    
    if (phone && !phoneRegex.test(phone)) {
        showInputError(input, 'Please enter a valid phone number');
        return false;
    } else {
        clearInputError(input);
        return true;
    }
}

function showInputError(input, message) {
    clearInputError(input);
    
    input.classList.add('border-red-500');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'text-red-500 text-sm mt-1';
    errorDiv.textContent = message;
    
    input.parentNode.appendChild(errorDiv);
}

function clearInputError(input) {
    input.classList.remove('border-red-500');
    const existingError = input.parentNode.querySelector('.text-red-500');
    if (existingError) {
        existingError.remove();
    }
}

// Image Lazy Loading
function initializeImageLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for older browsers
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Smooth Scrolling
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Toast Notifications
function initializeToastNotifications() {
    // Toast container will be created on first use
}

function showToast(message, type = 'info', duration = 3000) {
    let toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(toastContainer);
    }
    
    const toast = document.createElement('div');
    const typeClasses = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        warning: 'bg-yellow-500 text-white',
        info: 'bg-blue-500 text-white'
    };
    
    toast.className = `p-4 rounded-lg shadow-lg transform transition-transform duration-300 translate-x-full ${typeClasses[type] || typeClasses.info}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
        toast.classList.add('translate-x-0');
    }, 10);
    
    // Remove after duration
    setTimeout(() => {
        toast.classList.remove('translate-x-0');
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            toast.remove();
            if (toastContainer.children.length === 0) {
                toastContainer.remove();
            }
        }, 300);
    }, duration);
}

// Product Functions
function addToCart(productId, quantity = 1) {
    const formData = new FormData();
    formData.append('product_id', productId);
    formData.append('quantity', quantity);
    
    fetch('/add-to-cart', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Product added to cart!', 'success');
            updateCartCountDisplay();
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error adding product to cart', 'error');
    });
}

function updateCartCountDisplay() {
    const cartCountElements = document.querySelectorAll('.cart-count');
    const cart = JSON.parse(localStorage.getItem('somaliShopCart')) || [];
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    
    cartCountElements.forEach(element => {
        if (totalItems > 0) {
            element.textContent = totalItems;
            element.classList.remove('hidden');
        } else {
            element.classList.add('hidden');
        }
    });
}

// Admin Functions
function deleteProduct(productId, productName) {
    if (confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) {
        fetch('/admin/delete-product/' + productId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('Product deleted successfully!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error deleting product', 'error');
        });
    }
}

function deleteUser(userId, userEmail) {
    if (confirm(`Are you sure you want to delete user "${userEmail}"? This action cannot be undone.`)) {
        fetch('/admin/delete-user/' + userId, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showToast('User deleted successfully!', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showToast(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error deleting user', 'error');
        });
    }
}

// Export functions for global use
window.showToast = showToast;
window.addToCart = addToCart;
window.deleteProduct = deleteProduct;
window.deleteUser = deleteUser;

// Initialize WhatsApp links on page load
initializeWhatsAppLinks();