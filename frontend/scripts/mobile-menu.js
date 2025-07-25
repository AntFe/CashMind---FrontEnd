// Mobile Menu Handler
class MobileMenu {
    constructor() {
        this.sidebar = document.querySelector('.sidebar');
        this.menuBtn = document.querySelector('.mobile-menu-btn');
        this.overlay = document.querySelector('.sidebar-overlay');
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // Menu button click
        if (this.menuBtn) {
            this.menuBtn.addEventListener('click', () => this.toggle());
        }
        
        // Overlay click
        if (this.overlay) {
            this.overlay.addEventListener('click', () => this.close());
        }
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
        
        // Close on window resize to desktop
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && this.isOpen) {
                this.close();
            }
        });
        
        // Close on navigation click (mobile)
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    this.close();
                }
            });
        });
    }
    
    toggle() {
        this.isOpen ? this.close() : this.open();
    }
    
    open() {
        this.isOpen = true;
        this.sidebar.classList.add('active');
        this.overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Update button icon
        if (this.menuBtn) {
            this.menuBtn.innerHTML = '✕';
        }
    }
    
    close() {
        this.isOpen = false;
        this.sidebar.classList.remove('active');
        this.overlay.classList.remove('active');
        document.body.style.overflow = '';
        
        // Update button icon
        if (this.menuBtn) {
            this.menuBtn.innerHTML = '☰';
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    new MobileMenu();
});