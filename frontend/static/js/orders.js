Auth.requireLogin();

function orderCardHtml(order) {
  const items = order.items.map((i) => `${i.quantity} × ${i.product_name} (Rs. ${i.price_at_purchase})`).join('<br>');
  return `
    <div class="card" style="margin-bottom:14px;">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <strong>Order ${order.order_id.slice(0, 8)}...</strong>
        <span class="badge ${order.status}">${order.status}</span>
      </div>
      <p class="muted">${new Date(order.created_at).toLocaleString()}</p>
      <p>${items}</p>
      <strong>Total: Rs. ${order.total_amount}</strong>
    </div>`;
}

async function loadOrders() {
  const mount = document.getElementById('orders-mount');
  try {
    const data = await apiFetch('/orders/mine/');
    const items = data.results || data;
    mount.innerHTML = items.length
      ? items.map(orderCardHtml).join('')
      : '<p class="muted">No orders yet. <a href="products.html">Start shopping</a>.</p>';
  } catch (err) {
    showLoadError(mount, err, 'Unable to load your orders.');
  }
}

loadOrders();
