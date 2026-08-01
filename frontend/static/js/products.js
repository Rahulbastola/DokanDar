let currentPage = 1;

async function loadCategories() {
  try {
    const data = await apiFetch('/categories/');
    const select = document.getElementById('f-category');
    (data.results || data).forEach((cat) => {
      const opt = document.createElement('option');
      opt.value = cat.id;
      opt.textContent = cat.name;
      select.appendChild(opt);
    });
  } catch (err) {
    console.error(err);
  }
}

function buildQuery(page) {
  const params = new URLSearchParams();
  const search = document.getElementById('f-search').value.trim();
  const category = document.getElementById('f-category').value;
  const minPrice = document.getElementById('f-min-price').value;
  const maxPrice = document.getElementById('f-max-price').value;
  const minRating = document.getElementById('f-min-rating').value;
  const sort = document.getElementById('f-sort').value;

  if (search) params.set('search', search);
  if (category) params.set('category', category);
  if (minPrice) params.set('min_price', minPrice);
  if (maxPrice) params.set('max_price', maxPrice);
  if (minRating) params.set('min_rating', minRating);
  if (sort) params.set('sort', sort);
  params.set('page', page);
  return params.toString();
}

function renderStars(rating) {
  const rounded = Math.round(rating || 0);
  return '★'.repeat(rounded) + '☆'.repeat(5 - rounded);
}

async function loadProducts(page = 1) {
  currentPage = page;
  const grid = document.getElementById('product-grid');
  grid.innerHTML = '<p class="muted">Loading...</p>';
  try {
    const data = await apiFetch(`/products/?${buildQuery(page)}`);
    const items = data.results || data;
    if (!items.length) {
      grid.innerHTML = '<p class="muted">No products found.</p>';
    } else {
      grid.innerHTML = items.map(productCardHtml).join('');
      wireAddToCartButtons(grid);
    }
    renderPagination(data);
  } catch (err) {
    showLoadError(grid, err, 'Unable to load products.');
  }
}

const CART_ICON_SVG = `
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"
       stroke-linecap="round" stroke-linejoin="round">
    <circle cx="9" cy="21" r="1"></circle>
    <circle cx="20" cy="21" r="1"></circle>
    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
  </svg>`;

function productCardHtml(p) {
  const img = p.thumbnail || 'https://placehold.co/300x200?text=No+Image';
  const stockLine = p.stock > 0
    ? `<span class="muted">${p.stock} in stock</span>`
    : `<span class="muted" style="color:var(--danger);">Out of stock</span>`;
  return `
    <a class="product-card" href="product.html?id=${p.id}" style="color:inherit;">
      <div class="thumb-wrap">
        <img src="${img}" alt="${p.name}">
        ${p.stock === 0 ? '<span class="stock-ribbon">Sold out</span>' : ''}
      </div>
      <div class="body">
        <strong>${p.name}</strong>
        <span class="muted">${p.category_name} · by ${p.vendor_name}</span>
        <span class="rating">${renderStars(p.avg_rating)} (${p.review_count})</span>
        <div class="card-footer">
          <span class="price">Rs. ${p.price}</span>
          <button type="button" class="icon-btn add-to-cart-btn" data-product-id="${p.id}"
                  title="Add to cart" ${p.stock === 0 ? 'disabled' : ''}>${CART_ICON_SVG}</button>
        </div>
        ${stockLine}
      </div>
    </a>`;
}

async function addToCartFromGrid(productId, btn) {
  if (!Auth.requireLogin()) return;
  try {
    await apiFetch('/cart/add/', { method: 'POST', body: { product: Number(productId), quantity: 1 } });
    showToast('Added to cart.', 'success');
    btn.classList.add('added');
    setTimeout(() => btn.classList.remove('added'), 900);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

function wireAddToCartButtons(grid) {
  grid.querySelectorAll('.add-to-cart-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      addToCartFromGrid(btn.dataset.productId, btn);
    });
  });
}

function renderPagination(data) {
  const el = document.getElementById('pagination');
  el.innerHTML = '';
  if (!data.next && !data.previous) return;
  if (data.previous) {
    const btn = document.createElement('button');
    btn.className = 'btn secondary';
    btn.textContent = 'Previous';
    btn.onclick = () => loadProducts(currentPage - 1);
    el.appendChild(btn);
  }
  if (data.next) {
    const btn = document.createElement('button');
    btn.className = 'btn secondary';
    btn.textContent = 'Next';
    btn.onclick = () => loadProducts(currentPage + 1);
    el.appendChild(btn);
  }
}

document.getElementById('apply-filters').addEventListener('click', () => loadProducts(1));

loadCategories();
loadProducts();
