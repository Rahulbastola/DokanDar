Auth.requireLogin();
if (Auth.getUser().role !== 'super_admin') {
  window.location.href = 'products.html';
}

document.querySelectorAll('.tabs button').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tabs button').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    ['vendors', 'categories', 'orders'].forEach((tab) => {
      document.getElementById(`tab-${tab}`).style.display = tab === btn.dataset.tab ? 'block' : 'none';
    });
    if (btn.dataset.tab === 'orders') loadAllOrders();
  });
});

async function loadStats() {
  const mount = document.getElementById('stats-row');
  try {
    const stats = await apiFetch('/dashboard/stats/');
    mount.innerHTML = `
      <div class="stat-tile"><div class="value">Rs. ${stats.total_sales}</div><div class="label">Total Sales</div></div>
      <div class="stat-tile"><div class="value">${stats.total_orders}</div><div class="label">Total Orders</div></div>
      <div class="stat-tile"><div class="value">${stats.total_users}</div><div class="label">Total Customers</div></div>
      <div class="stat-tile"><div class="value">${stats.total_admins}</div><div class="label">Total Vendors</div></div>
    `;
    if (stats.sales_by_vendor.length) {
      mount.insertAdjacentHTML('afterend', `
        <div class="card" style="margin-bottom:24px;">
          <h3>Sales by Vendor</h3>
          <table>
            <thead><tr><th>Vendor</th><th>Orders</th><th>Items Sold</th><th>Sales</th></tr></thead>
            <tbody>
              ${stats.sales_by_vendor.map((v) => `
                <tr>
                  <td>${v.product__created_by__username}</td>
                  <td>${v.order_count}</td>
                  <td>${v.items_sold}</td>
                  <td>Rs. ${v.total_sales}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>`);
    }
  } catch (err) {
    showLoadError(mount, err, 'Unable to load dashboard stats.');
  }
}

async function loadPendingVendors() {
  const mount = document.getElementById('pending-vendors-mount');
  try {
    const data = await apiFetch('/auth/vendors/pending/');
    const items = data.results || data;
    mount.innerHTML = items.length ? `
      <table>
        <thead><tr><th>Username</th><th>Email</th><th>Registered</th><th></th></tr></thead>
        <tbody>
          ${items.map((v) => `
            <tr>
              <td>${v.username}</td>
              <td>${v.email}</td>
              <td>${new Date(v.date_joined).toLocaleDateString()}</td>
              <td style="display:flex; gap:6px;">
                <button class="btn" data-approve-id="${v.id}">Approve</button>
                <button class="btn danger" data-reject-id="${v.id}">Reject</button>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>` : '<p class="muted">No pending vendor approvals.</p>';

    mount.querySelectorAll('[data-approve-id]').forEach((btn) =>
      btn.addEventListener('click', () => approveVendor(btn.dataset.approveId)));
    mount.querySelectorAll('[data-reject-id]').forEach((btn) =>
      btn.addEventListener('click', () => rejectVendor(btn.dataset.rejectId)));
  } catch (err) {
    showLoadError(mount, err, 'Unable to load pending vendors.');
  }
}

async function approveVendor(id) {
  try {
    await apiFetch(`/auth/vendors/${id}/approve/`, { method: 'POST' });
    showToast('Vendor approved.', 'success');
    loadPendingVendors();
    loadStats();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function rejectVendor(id) {
  if (!confirm('Reject and delete this pending vendor account?')) return;
  try {
    await apiFetch(`/auth/vendors/${id}/approve/`, { method: 'DELETE' });
    showToast('Vendor registration rejected.', 'success');
    loadPendingVendors();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadCategories() {
  const mount = document.getElementById('category-list-mount');
  try {
    const data = await apiFetch('/categories/');
    const items = data.results || data;
    mount.innerHTML = `
      <table>
        <thead><tr><th>Name</th><th>Description</th></tr></thead>
        <tbody>${items.map((c) => `<tr><td>${c.name}</td><td>${c.description || ''}</td></tr>`).join('')}</tbody>
      </table>`;
  } catch (err) {
    showLoadError(mount, err, 'Unable to load categories.');
  }
}

document.getElementById('category-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const formData = new FormData(e.target);
  try {
    await apiFetch('/categories/', { method: 'POST', body: Object.fromEntries(formData.entries()) });
    showToast('Category added.', 'success');
    e.target.reset();
    loadCategories();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

async function loadAllOrders() {
  const mount = document.getElementById('all-orders-mount');
  const params = new URLSearchParams();
  const status = document.getElementById('of-status').value;
  const from = document.getElementById('of-from').value;
  const to = document.getElementById('of-to').value;
  if (status) params.set('status', status);
  if (from) params.set('date_from', from);
  if (to) params.set('date_to', to);

  try {
    const data = await apiFetch(`/orders/all/?${params.toString()}`);
    const items = data.results || data;
    mount.innerHTML = items.length ? `
      <table>
        <thead><tr><th>Order</th><th>Customer</th><th>Items</th><th>Total</th><th>Status</th><th>Date</th></tr></thead>
        <tbody>
          ${items.map((o) => `
            <tr>
              <td>${o.order_id.slice(0, 8)}...</td>
              <td>${o.username}</td>
              <td>${o.items.map((i) => `${i.quantity} × ${i.product_name}`).join('<br>')}</td>
              <td>Rs. ${o.total_amount}</td>
              <td><span class="badge ${o.status}">${o.status}</span></td>
              <td>${new Date(o.created_at).toLocaleDateString()}</td>
            </tr>`).join('')}
        </tbody>
      </table>` : '<p class="muted">No orders found.</p>';
  } catch (err) {
    showLoadError(mount, err, 'Unable to load orders.');
  }
}

document.getElementById('of-apply').addEventListener('click', loadAllOrders);

loadStats();
loadPendingVendors();
loadCategories();
