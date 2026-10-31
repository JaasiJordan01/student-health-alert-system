// Small, lightweight interactive logic for the prototype.

document.addEventListener('DOMContentLoaded', function () {
  const alertCards = document.querySelectorAll('.alert-item');
  alertCards.forEach((card) => {
    card.addEventListener('click', () => {
      card.style.transform = 'translateY(-2px)';
      card.style.boxShadow = '0 8px 18px rgba(15, 23, 42, 0.08)';
    });
  });
});
