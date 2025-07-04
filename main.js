let cartCount = 0;

document.querySelectorAll('.add-to-cart-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    cartCount++;
    // Update badge
    const badge = document.getElementById('cart-badge');
    badge.textContent = cartCount;
    badge.style.display = 'inline-block';

    // Show notification
    const notification = document.getElementById('notification');
    notification.textContent = `${this.dataset.product} added to cart!`;
    notification.style.display = 'block';
    setTimeout(() => {
      notification.style.display = 'none';
    }, 2000);
  });
});