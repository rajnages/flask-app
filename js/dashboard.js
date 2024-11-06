document.addEventListener('DOMContentLoaded', function() {
    // Menu item activation
    const menuItems = document.querySelectorAll('.menu-item');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Notifications popup
    const notificationBell = document.querySelector('.notifications');
    notificationBell.addEventListener('click', function() {
        // Add notification popup functionality
    });

    // Search functionality
    const searchInput = document.querySelector('.search input');
    searchInput.addEventListener('input', function() {
        // Add search functionality
    });

    // Update server time
    function updateServerTime() {
        const timeElement = document.querySelector('.info-item span:last-child');
        if (timeElement) {
            const now = new Date();
            timeElement.textContent = now.toLocaleString();
        }
    }
    setInterval(updateServerTime, 1000);
});