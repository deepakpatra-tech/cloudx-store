
// ============================================
// CLOUDX STORE - FRONTEND APPLICATION
// Backend: Flask
// Database: PostgreSQL
// ============================================

// APPLICATION STATE

let products = [];
let currentUser = null;
let cart = [];

try {
    cart = JSON.parse(localStorage.getItem("cloudx-cart")) || [];
    if (!Array.isArray(cart)) cart = [];
} catch {
    cart = [];
}

// ============================================
// API HELPER
// ============================================

async function api(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || data.message || "Something went wrong");
    }

    return data;
}

// ============================================
// COMMON FUNCTIONS
// ============================================

function money(amount) {
    return "₹" + Number(amount).toFixed(2);
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

function saveCart() {
    localStorage.setItem("cloudx-cart", JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    const count = cart.reduce(
        (total, item) => total + Number(item.quantity),
        0
    );

    document.getElementById("cart-count").textContent = count;
}

function updateNavigation() {
    document.getElementById("logout-btn").style.display =
        currentUser ? "inline-block" : "none";

    const ordersButton = document.getElementById("my-orders-btn");

    if (ordersButton) {
        ordersButton.style.display =
            currentUser ? "inline-block" : "none";
    }
}

// ============================================
// PAGE NAVIGATION
// ============================================

async function showPage(pageName) {
    const publicPages = ["login", "register"];

    if (!publicPages.includes(pageName) && !currentUser) {
        pageName = "login";
    }

    document.querySelectorAll(".page").forEach(page => {
        page.style.display = "none";
    });

    const selectedPage = document.getElementById(pageName + "-page");

    if (!selectedPage) {
        return;
    }

    selectedPage.style.display =
        publicPages.includes(pageName) ? "flex" : "block";

    if (pageName === "products") {
        await loadProducts();
    }

    if (pageName === "cart") {
        renderCart();
    }

    if (pageName === "checkout") {
        updateCheckoutTotal();
    }

    if (pageName === "my-orders") {
        await loadMyOrders();
    }
}

// ============================================
// REGISTRATION
// ============================================

document.getElementById("register-form").addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        const name = document.getElementById("register-name").value.trim();
        const email = document.getElementById("register-email").value.trim();
        const password = document.getElementById("register-password").value;

        const message = document.getElementById("register-message");
        const button = this.querySelector("button");

        if (name.length < 2 || password.length < 8) {
            message.textContent =
                "Enter a valid name and password of at least 8 characters.";
            return;
        }

        button.disabled = true;
        button.textContent = "Creating account...";
        message.textContent = "";

        try {
            const data = await api("/api/register", {
                method: "POST",
                body: JSON.stringify({ name, email, password })
            });

            message.style.color = "green";
            message.textContent = data.message || "Registration successful.";

            this.reset();

            setTimeout(() => {
                message.style.color = "";
                showPage("login");
            }, 1200);

        } catch (error) {
            message.style.color = "red";
            message.textContent = error.message;

        } finally {
            button.disabled = false;
            button.textContent = "Create Account";
        }
    }
);

// ============================================
// LOGIN
// ============================================

document.getElementById("login-form").addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        const message = document.getElementById("login-message");
        const button = this.querySelector("button");

        button.disabled = true;
        button.textContent = "Logging in...";
        message.textContent = "";

        try {
            const data = await api("/api/login", {
                method: "POST",
                body: JSON.stringify({ email, password })
            });

            currentUser = data.user;

            updateNavigation();
            this.reset();

            await showPage("products");

        } catch (error) {
            message.textContent = error.message;

        } finally {
            button.disabled = false;
            button.textContent = "Login";
        }
    }
);

// ============================================
// LOAD PRODUCTS
// ============================================

async function loadProducts() {
    const container = document.getElementById("product-list");

    container.innerHTML = "<p>Loading products...</p>";

    try {
        products = await api("/api/products");
        renderProducts();

    } catch (error) {
        container.innerHTML =
            `<p>Unable to load products: ${escapeHTML(error.message)}</p>`;
    }
}

// ============================================
// DISPLAY PRODUCTS
// ============================================

function renderProducts() {
    const container = document.getElementById("product-list");

    if (!products.length) {
        container.innerHTML = "<p>No products available.</p>";
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="product-card">
            <img
                src="${escapeHTML(product.image || "https://placehold.co/600x400?text=Product")}"
                alt="${escapeHTML(product.name)}"
                onerror="this.src='https://placehold.co/600x400?text=Product'"
            >

            <div class="product-info">
                <h3>${escapeHTML(product.name)}</h3>
                <p>${escapeHTML(product.description || "")}</p>
                <div class="product-price">${money(product.price)}</div>

                <button onclick="addToCart(${Number(product.id)})">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join("");
}

// ============================================
// ADD PRODUCT TO CART
// ============================================

function addToCart(productId) {
    const product = products.find(
        item => Number(item.id) === Number(productId)
    );

    if (!product) {
        alert("Product not found.");
        return;
    }

    const existingItem = cart.find(
        item => Number(item.id) === Number(productId)
    );

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.push({
            id: Number(productId),
            quantity: 1
        });
    }

    saveCart();
    alert("Product added to cart.");
}

// ============================================
// RENDER SHOPPING CART
// ============================================

function renderCart() {
    const container = document.getElementById("cart-items");
    let subtotal = 0;

    if (!cart.length) {
        container.innerHTML = "<p>Your shopping cart is empty.</p>";

        document.getElementById("subtotal").textContent = money(0);
        document.getElementById("shipping").textContent = money(0);
        document.getElementById("total").textContent = money(0);
        document.getElementById("checkout-btn").disabled = true;

        return;
    }

    document.getElementById("checkout-btn").disabled = false;

    container.innerHTML = cart.map(item => {
        const product = products.find(
            p => Number(p.id) === Number(item.id)
        );

        if (!product) return "";

        const quantity = Number(item.quantity);
        const itemTotal = Number(product.price) * quantity;

        subtotal += itemTotal;

        return `
            <div class="cart-item">
                <div>
                    <h3>${escapeHTML(product.name)}</h3>
                    <p>${money(product.price)} each</p>
                </div>

                <div>
                    <input
                        type="number"
                        min="1"
                        max="99"
                        value="${quantity}"
                        onchange="updateQuantity(${Number(item.id)}, this.value)"
                    >
                </div>

                <div><strong>${money(itemTotal)}</strong></div>

                <button onclick="removeFromCart(${Number(item.id)})">
                    Remove
                </button>
            </div>
        `;
    }).join("");

    const shipping = 50;

    document.getElementById("subtotal").textContent = money(subtotal);
    document.getElementById("shipping").textContent = money(shipping);
    document.getElementById("total").textContent =
        money(subtotal + shipping);
}

// ============================================
// UPDATE PRODUCT QUANTITY
// ============================================

function updateQuantity(productId, quantity) {
    quantity = Number(quantity);

    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 99) {
        alert("Quantity must be between 1 and 99.");
        renderCart();
        return;
    }

    const item = cart.find(
        item => Number(item.id) === Number(productId)
    );

    if (item) {
        item.quantity = quantity;
    }

    saveCart();
    renderCart();
}

// ============================================
// REMOVE PRODUCT FROM CART
// ============================================

function removeFromCart(productId) {
    cart = cart.filter(
        item => Number(item.id) !== Number(productId)
    );

    saveCart();
    renderCart();
}

// ============================================
// CHECKOUT TOTAL
// ============================================

function updateCheckoutTotal() {
    let subtotal = 0;

    cart.forEach(item => {
        const product = products.find(
            p => Number(p.id) === Number(item.id)
        );

        if (product) {
            subtotal += Number(product.price) * Number(item.quantity);
        }
    });

    document.getElementById("checkout-total").textContent =
        money(subtotal + 50);
}

// ============================================
// PLACE ORDER
// ============================================

document.getElementById("checkout-form").addEventListener(
    "submit",
    async function (event) {
        event.preventDefault();

        if (!cart.length) {
            alert("Your cart is empty.");
            return;
        }

        const customerName =
            document.getElementById("customer-name").value.trim();

        const phone =
            document.getElementById("phone").value.trim();

        const address =
            document.getElementById("address").value.trim();

        const paymentMethod =
            document.getElementById("payment-method").value;

        const message = document.getElementById("checkout-message");
        const button = document.getElementById("place-order-btn");

        button.disabled = true;
        button.textContent = "Placing order...";
        message.textContent = "";

        try {
            const data = await api("/api/orders", {
                method: "POST",
                body: JSON.stringify({
                    customer_name: customerName,
                    phone,
                    address,
                    payment_method: paymentMethod,
                    items: cart.map(item => ({
                        product_id: Number(item.id),
                        quantity: Number(item.quantity)
                    }))
                })
            });

            cart = [];
            saveCart();

            document.getElementById("order-id").textContent =
                data.order_id;

            this.reset();

            await showPage("success");

        } catch (error) {
            message.textContent = error.message;

        } finally {
            button.disabled = false;
            button.textContent = "Place Order";
        }
    }
);

// ============================================
// MY ORDERS - LOAD FROM BACKEND
// ============================================

async function loadMyOrders() {
    const container = document.getElementById("my-orders-list");

    container.innerHTML = "<p>Loading your orders...</p>";

    try {
        const data = await api("/api/my-orders");

        renderMyOrders(data.orders || []);

    } catch (error) {
        container.innerHTML = `
            <div class="orders-empty">
                <h3>Unable to load orders</h3>
                <p>${escapeHTML(error.message)}</p>
                <button onclick="loadMyOrders()">Try Again</button>
            </div>
        `;
    }
}

// ============================================
// DISPLAY ORDER HISTORY
// ============================================

function renderMyOrders(orders) {
    const container = document.getElementById("my-orders-list");

    if (!orders.length) {
        container.innerHTML = `
            <div class="orders-empty">
                <h2>No orders yet</h2>
                <p>Your placed orders will appear here.</p>
                <button onclick="showPage('products')">
                    Start Shopping
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = orders.map(order => {
        const status = String(order.status || "Pending");
        const statusClass = status.toLowerCase().replace(/[^a-z0-9]+/g, "-");

        const orderDate = order.created_at
            ? new Date(order.created_at).toLocaleString("en-IN", {
                dateStyle: "medium",
                timeStyle: "short"
            })
            : "Date unavailable";

        const itemsHTML = (order.items || []).map(item => `
            <div class="order-item">
                <img
                    src="${escapeHTML(item.image || "https://placehold.co/100x100?text=Product")}"
                    alt="${escapeHTML(item.name)}"
                    onerror="this.src='https://placehold.co/100x100?text=Product'"
                >

                <div class="order-item-details">
                    <h4>${escapeHTML(item.name)}</h4>
                    <p>Quantity: ${Number(item.quantity)}</p>
                    <p>Price: ${money(item.price)}</p>
                </div>

                <strong>
                    ${money(Number(item.price) * Number(item.quantity))}
                </strong>
            </div>
        `).join("");

        return `
            <article class="order-card">

                <div class="order-header">
                    <div>
                        <h3>Order #${Number(order.order_id)}</h3>
                        <p>${escapeHTML(orderDate)}</p>
                    </div>

                    <span class="order-status status-${escapeHTML(statusClass)}">
                        ${escapeHTML(status)}
                    </span>
                </div>

                <div class="order-products">
                    ${itemsHTML}
                </div>

                <div class="order-footer">
                    <div>
                        <p>Payment: ${escapeHTML(order.payment_method)}</p>
                        <p>Delivery to: ${escapeHTML(order.address)}</p>
                    </div>

                    <div class="order-total">
                        <span>Order Total</span>
                        <strong>${money(order.total)}</strong>
                    </div>
                </div>

            </article>
        `;
    }).join("");
}

// ============================================
// LOGOUT
// ============================================

async function logout() {
    try {
        await api("/api/logout", {
            method: "POST"
        });

        currentUser = null;

        updateNavigation();
        await showPage("login");

    } catch (error) {
        alert(error.message);
    }
}

// ============================================
// APPLICATION INITIALIZATION
// ============================================

async function initializeApp() {
    updateCartCount();
    updateNavigation();

    try {
        const sessionData = await api("/api/session");

        currentUser = sessionData.user;

        updateNavigation();
        await showPage("products");

    } catch (error) {
        currentUser = null;

        updateNavigation();
        await showPage("login");
    }
}

// START APPLICATION

initializeApp();
