Auth.requireLogin();
const user = Auth.getUser();
if (user.role !== 'admin') {
  window.location.href = 'products.html';
}

let editingId = null;

document.querySelectorAll('.tabs button').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tabs button').forEach((b) => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-products').style.display = btn.dataset.tab === 'products' ? 'block' : 'none';
    document.getElementById('tab-orders').style.display = btn.dataset.tab === 'orders' ? 'block' : 'none';
    if (btn.dataset.tab === 'orders') loadVendorOrders();
  });
});

async function checkApproval() {
  if (!user.is_approved) {
    document.getElementById('pending-banner').innerHTML =
      '<div class="alert error">Your vendor account is pending approval by a super admin. You cannot manage products yet.</div>';
    document.getElementById('product-form').querySelectorAll('input,textarea,select,button').forEach((el) => el.disabled = true);
  }
}

async function loadCategoriesIntoForm() {
  try {
    const data = await apiFetch('/categories/');
    const select = document.getElementById('category-select');
    select.innerHTML = (data.results || data).map((c) => `<option value="${c.id}">${c.name}</option>`).join('');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function loadMyProducts() {
  const mount = document.getElementById('product-list');
  try {
    const data = await apiFetch(`/products/?vendor=${user.id}`);
    const items = data.results || data;
    mount.innerHTML = items.length ? `
      <table>
        <thead>
          <tr>
            <th></th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th>
            <th>Rating</th><th>Status</th><th></th>
          </tr>
        </thead>
        <tbody>${items.map(vendorProductRowHtml).join('')}</tbody>
      </table>` : '<p class="muted">You have not added any products yet.</p>';

    mount.querySelectorAll('[data-edit-id]').forEach((btn) => btn.addEventListener('click', () => startEdit(btn.dataset.editId)));
    mount.querySelectorAll('[data-delete-id]').forEach((btn) => btn.addEventListener('click', () => deleteProduct(btn.dataset.deleteId)));
  } catch (err) {
    showLoadError(mount, err, 'Unable to load your products.');
  }
}

function vendorProductRowHtml(p) {
  const img = p.thumbnail || 'https://placehold.co/60x60?text=No+Image';
  return `
    <tr>
      <td><img src="${img}" alt="${p.name}" style="width:48px; height:48px; object-fit:cover; border-radius:6px;"></td>
      <td>${p.name}</td>
      <td>${p.category_name}</td>
      <td>Rs. ${p.price}</td>
      <td>${p.stock}</td>
      <td>${p.avg_rating ? p.avg_rating.toFixed(1) : '—'} (${p.review_count})</td>
      <td><span class="badge ${p.is_active ? 'paid' : 'cancelled'}">${p.is_active ? 'Active' : 'Inactive'}</span></td>
      <td style="white-space:nowrap;">
        <button class="btn secondary" data-edit-id="${p.id}">Edit</button>
        <button class="btn danger" data-delete-id="${p.id}">Delete</button>
      </td>
    </tr>`;
}

async function startEdit(id) {
  try {
    const p = await apiFetch(`/products/${id}/`);
    editingId = id;
    const form = document.getElementById('product-form');
    form.name.value = p.name;
    form.description.value = p.description;
    form.price.value = p.price;
    form.stock.value = p.stock;
    form.category.value = p.category;
    document.getElementById('is-active-checkbox').checked = p.is_active;
    document.getElementById('form-title').textContent = `Edit Product: ${p.name}`;
    document.getElementById('cancel-edit').style.display = 'inline-block';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('cancel-edit').addEventListener('click', resetForm);

function resetForm() {
  editingId = null;
  document.getElementById('product-form').reset();
  document.getElementById('form-title').textContent = 'Add Product';
  document.getElementById('cancel-edit').style.display = 'none';
}

async function deleteProduct(id) {
  if (!confirm('Delete this product?')) return;
  try {
    await apiFetch(`/products/${id}/`, { method: 'DELETE' });
    showToast('Product deleted.', 'success');
    loadMyProducts();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

document.getElementById('product-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  formData.delete('id');
  if (!formData.get('uploaded_images') || formData.get('uploaded_images').size === 0) {
    formData.delete('uploaded_images');
  }
  formData.set('is_active', document.getElementById('is-active-checkbox').checked ? 'true' : 'false');

  try {
    if (editingId) {
      await apiFetch(`/products/${editingId}/`, { method: 'PATCH', body: formData });
      showToast('Product updated.', 'success');
    } else {
      await apiFetch('/products/', { method: 'POST', body: formData });
      showToast('Product created.', 'success');
    }
    resetForm();
    loadMyProducts();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

async function loadVendorOrders() {
  const mount = document.getElementById('vendor-orders-mount');
  try {
    const data = await apiFetch('/orders/vendor/');
    const items = data.results || data;
    mount.innerHTML = items.length ? `
      <table>
        <thead><tr><th>Order</th><th>Customer</th><th>Items</th><th>Status</th><th>Date</th></tr></thead>
        <tbody>
          ${items.map((o) => `
            <tr>
              <td>${o.order_id.slice(0, 8)}...</td>
              <td>${o.username}</td>
              <td>${o.items.map((i) => `${i.quantity} × ${i.product_name}`).join('<br>')}</td>
              <td><span class="badge ${o.status}">${o.status}</span></td>
              <td>${new Date(o.created_at).toLocaleDateString()}</td>
            </tr>`).join('')}
        </tbody>
      </table>` : '<p class="muted">No orders yet.</p>';
  } catch (err) {
    showLoadError(mount, err, 'Unable to load your orders.');
  }
}

checkApproval();
loadCategoriesIntoForm();
loadMyProducts();
