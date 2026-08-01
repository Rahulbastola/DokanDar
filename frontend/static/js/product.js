const productId = new URLSearchParams(window.location.search).get('id');

function stars(rating) {
  const rounded = Math.round(rating || 0);
  return '★'.repeat(rounded) + '☆'.repeat(5 - rounded);
}

async function loadProduct() {
  const mount = document.getElementById('product-detail');
  try {
    const p = await apiFetch(`/products/${productId}/`);
    const images = p.images.length
      ? p.images.map((img) => `<img src="${img.image}" alt="${p.name}" data-full="${img.image}">`).join('')
      : '';
    const mainImg = p.images.length ? p.images[0].image : 'https://placehold.co/500x400?text=No+Image';

    mount.innerHTML = `
      <div>
        <img class="main-image" src="${mainImg}" alt="${p.name}">
        <div class="gallery">${images}</div>
      </div>
      <div>
        <h2>${p.name}</h2>
        <p class="muted">${p.category_name} · sold by ${p.vendor_name}</p>
        <p class="rating">${stars(p.avg_rating)} (${p.review_count} reviews)</p>
        <p class="price" style="font-size:1.4rem;">Rs. ${p.price}</p>
        <p>${p.description || ''}</p>
        <p class="muted">${p.stock > 0 ? p.stock + ' in stock' : 'Out of stock'}</p>
        <div style="display:flex; gap:8px; align-items:center; margin-top:12px;">
          <input type="number" id="qty" value="1" min="1" max="${p.stock}" style="width:70px; padding:6px;">
          <button class="btn" id="add-to-cart-btn" ${p.stock === 0 ? 'disabled' : ''}>Add to Cart</button>
        </div>
      </div>
    `;

    document.getElementById('add-to-cart-btn')?.addEventListener('click', addToCart);
    document.querySelectorAll('.gallery img').forEach((thumb) => {
      thumb.addEventListener('click', () => {
        document.querySelector('.main-image').src = thumb.dataset.full;
      });
    });
    renderReviews(p.reviews);
    renderReviewForm();
  } catch (err) {
    showLoadError(mount, err, 'Unable to load this product.');
  }
}

function renderReviews(reviews) {
  const list = document.getElementById('review-list');
  if (!reviews.length) {
    list.innerHTML = '<p class="muted">No reviews yet.</p>';
    return;
  }
  list.innerHTML = reviews.map((r) => `
    <div class="review-item">
      <strong>${r.user}</strong> <span class="stars">${stars(r.rating)}</span>
      <p>${r.comment || ''}</p>
      <span class="muted">${new Date(r.created_at).toLocaleDateString()}</span>
    </div>
  `).join('');
}

function renderReviewForm() {
  const mount = document.getElementById('review-form-mount');
  if (!Auth.isLoggedIn()) {
    mount.innerHTML = '<p class="muted"><a href="login.html">Login</a> to leave a review (purchase required).</p>';
    return;
  }
  mount.innerHTML = `
    <h4 style="margin-top:20px;">Leave a review</h4>
    <form class="stacked" id="review-form">
      <label>Rating</label>
      <select name="rating">
        <option value="5">5 - Excellent</option>
        <option value="4">4 - Good</option>
        <option value="3">3 - Average</option>
        <option value="2">2 - Poor</option>
        <option value="1">1 - Terrible</option>
      </select>
      <label>Comment</label>
      <textarea name="comment" rows="3"></textarea>
      <button class="btn" type="submit">Submit Review</button>
    </form>
  `;
  document.getElementById('review-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
      await apiFetch(`/products/${productId}/reviews/`, {
        method: 'POST',
        body: { rating: Number(formData.get('rating')), comment: formData.get('comment') },
      });
      showToast('Review submitted.', 'success');
      loadProduct();
    } catch (err) {
      showToast(err.message, 'error');
    }
  });
}

async function addToCart() {
  if (!Auth.requireLogin()) return;
  const quantity = Number(document.getElementById('qty').value) || 1;
  try {
    await apiFetch('/cart/add/', { method: 'POST', body: { product: Number(productId), quantity } });
    showToast('Added to cart.', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  }
}

loadProduct();
