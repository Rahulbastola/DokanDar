Auth.requireLogin();

async function loadCart() {
  const mount = document.getElementById('cart-mount');
  try {
    const cart = await apiFetch('/cart/');
    if (!cart.items.length) {
      mount.innerHTML = '<p class="muted">Your cart is empty. <a href="products.html">Browse products</a>.</p>';
      return;
    }
    mount.innerHTML = `
      <table>
        <thead><tr><th>Product</th><th>Price</th><th>Quantity</th><th>Subtotal</th><th></th></tr></thead>
        <tbody>
          ${cart.items.map((item) => `
            <tr>
              <td>${item.product_name}</td>
              <td>Rs. ${item.price}</td>
              <td><input type="number" min="1" value="${item.quantity}" data-item-id="${item.id}" class="qty-input" style="width:60px; padding:4px;"></td>
              <td>Rs. ${item.subtotal.toFixed ? item.subtotal.toFixed(2) : item.subtotal}</td>
              <td><button class="btn danger" data-remove-id="${item.id}">Remove</button></td>
            </tr>`).join('')}
        </tbody>
      </table>
      <div style="text-align:right; margin-top:16px;">
        <strong>Total: Rs. ${cart.total}</strong><br>
        <button class="btn" id="checkout-btn" style="margin-top:10px;">Checkout with eSewa</button>
      </div>
    `;

    mount.querySelectorAll('.qty-input').forEach((input) => {
      input.addEventListener('change', () => updateQuantity(input.dataset.itemId, input.value));
    });
    mount.querySelectorAll('[data-remove-id]').forEach((btn) => {
      btn.addEventListener('click', () => removeItem(btn.dataset.removeId));
    });
    document.getElementById('checkout-btn').addEventListener('click', checkout);
  } catch (err) {
    showLoadError(mount, err, 'Unable to load your cart.');
  }
}

async function updateQuantity(itemId, quantity) {
  try {
    await apiFetch(`/cart/items/${itemId}/`, { method: 'PATCH', body: { quantity: Number(quantity) } });
    loadCart();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function removeItem(itemId) {
  try {
    await apiFetch(`/cart/items/${itemId}/`, { method: 'DELETE' });
    loadCart();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function checkout() {
  try {
    const data = await apiFetch('/orders/checkout/', { method: 'POST' });
    submitToEsewa(data.esewa);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function submitToEsewa(fields) {
  const form = document.createElement('form');
  form.method = 'POST';
  form.action = fields.payment_url;

  Object.entries(fields).forEach(([key, value]) => {
    if (key === 'payment_url') return;
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = key;
    input.value = value;
    form.appendChild(input);
  });

  document.body.appendChild(form);
  form.submit();
}

loadCart();
