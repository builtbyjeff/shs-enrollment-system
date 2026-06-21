// ── Expand/Collapse student card details ──
function toggleExpand(btn) {
  const card    = btn.closest('.student-card');
  const section = card.querySelector('.student-expand');
  const icon    = btn.querySelector('i');

  section.classList.toggle('hidden');
  if (section.classList.contains('hidden')) {
    icon.className = 'fas fa-chevron-down';
    btn.innerHTML  = '<i class="fas fa-chevron-down"></i> View More';
  } else {
    btn.innerHTML  = '<i class="fas fa-chevron-up"></i> View Less';
  }
}

// ── Toggle password visibility ──
function togglePw() {
  const input  = document.getElementById('passwordField');
  const icon   = document.getElementById('pwIcon');
  if (input.type === 'password') {
    input.type   = 'password' === 'password' ? 'text' : 'password';
    input.type   = 'text';
    icon.className = 'fas fa-eye-slash';
  } else {
    input.type   = 'password';
    icon.className = 'fas fa-eye';
  }
}

// ── Auto-dismiss alerts after 4 seconds ──
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity .5s';
      alert.style.opacity    = '0';
      setTimeout(() => alert.remove(), 500);
    }, 4000);
  });

  // Scroll to alert if exists
  const firstAlert = document.querySelector('.alert');
  if (firstAlert) {
    firstAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
});



