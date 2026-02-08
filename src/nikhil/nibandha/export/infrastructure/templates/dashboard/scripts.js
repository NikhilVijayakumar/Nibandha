// Theme Toggle
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    body.setAttribute('data-theme', newTheme);
    
    const btn = document.querySelector('.theme-toggle .text');
    btn.textContent = newTheme === 'light' ? 'Dark Mode' : 'Light Mode';
    
    const icon = document.querySelector('.theme-toggle .icon');
    icon.textContent = newTheme === 'light' ? '🌙' : '☀️';
    
    localStorage.setItem('theme', newTheme);
}

// Load saved theme
const savedTheme = localStorage.getItem('theme') || 'light';
document.body.setAttribute('data-theme', savedTheme);
if (savedTheme === 'dark') {
    document.querySelector('.theme-toggle .text').textContent = 'Light Mode';
    document.querySelector('.theme-toggle .icon').textContent = '☀️';
}

// Smooth scrolling for navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href');
        const targetSection = document.querySelector(targetId);
        
        // Remove active class from all links
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        
        // Add active class to clicked link
        this.classList.add('active');
        
        // Smooth scroll to section
        targetSection.scrollIntoView({ behavior: 'smooth' });
    });
});

// Set first link as active on load
document.querySelector('.nav-link')?.classList.add('active');

// Export PDF function (placeholder)
function exportPDF() {
    window.print();
}

// Intersection Observer for active nav highlighting
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${id}`) {
                    link.classList.add('active');
                }
            });
        }
    });
}, { threshold: 0.5 });

document.querySelectorAll('.content-section').forEach(section => {
    observer.observe(section);
});
