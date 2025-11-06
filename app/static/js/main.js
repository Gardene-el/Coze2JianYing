// Main JavaScript for Coze2JianYing Website

document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('.nav-menu a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all sections
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(section);
    });

    // Highlight current section in navigation
    window.addEventListener('scroll', function() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - 60) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });

    // Add hover effect to cards
    const cards = document.querySelectorAll('.feature-card, .api-link, .status-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Copy code snippet functionality
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = '复制';
        copyButton.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8rem;
        `;

        const pre = block.parentElement;
        pre.style.position = 'relative';
        pre.appendChild(copyButton);

        copyButton.addEventListener('click', function() {
            const text = block.textContent;
            navigator.clipboard.writeText(text).then(() => {
                copyButton.textContent = '已复制!';
                setTimeout(() => {
                    copyButton.textContent = '复制';
                }, 2000);
            });
        });
    });

    // Mobile menu toggle (if needed in future)
    const createMobileMenu = function() {
        const navMenu = document.querySelector('.nav-menu');
        const toggleButton = document.createElement('button');
        toggleButton.className = 'mobile-menu-toggle';
        toggleButton.innerHTML = '☰';
        toggleButton.style.cssText = `
            display: none;
            font-size: 1.5rem;
            background: none;
            border: none;
            cursor: pointer;
            color: var(--text-dark);
        `;

        // Show toggle button on mobile
        if (window.innerWidth <= 768) {
            toggleButton.style.display = 'block';
            const navbar = document.querySelector('.navbar .container');
            navbar.insertBefore(toggleButton, navMenu);

            toggleButton.addEventListener('click', function() {
                navMenu.classList.toggle('show');
            });
        }
    };

    createMobileMenu();

    // Check API server status
    const checkAPIStatus = async function() {
        try {
            const response = await fetch('/api/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                console.log('API 服务正常运行');
                // Optionally show status indicator
                const statusIndicator = document.createElement('div');
                statusIndicator.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: var(--secondary-color);
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    box-shadow: var(--shadow);
                    font-size: 0.9rem;
                    z-index: 1000;
                `;
                statusIndicator.textContent = '🟢 API 服务运行中';
                document.body.appendChild(statusIndicator);
                
                // Auto-hide after 3 seconds
                setTimeout(() => {
                    statusIndicator.style.opacity = '0';
                    statusIndicator.style.transition = 'opacity 0.5s ease';
                    setTimeout(() => statusIndicator.remove(), 500);
                }, 3000);
            }
        } catch (error) {
            console.log('API 服务未启动或不可访问');
        }
    };

    // Check API status on page load
    checkAPIStatus();

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus on search (if implemented)
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            // Future: implement search functionality
        }
    });

    // Track page analytics (if needed)
    const trackPageView = function() {
        // Future: integrate analytics
        console.log('Page loaded:', window.location.pathname);
    };

    trackPageView();

    // Easter egg: Konami code
    let konamiCode = [];
    const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    
    document.addEventListener('keydown', function(e) {
        konamiCode.push(e.key);
        konamiCode = konamiCode.slice(-10);
        
        if (konamiCode.join('') === konamiSequence.join('')) {
            // Easter egg activated!
            const hero = document.querySelector('.hero');
            hero.style.background = 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)';
            
            const message = document.createElement('div');
            message.textContent = '🎉 彩蛋激活！感谢你的探索精神！';
            message.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 2rem;
                border-radius: 10px;
                box-shadow: var(--shadow-hover);
                font-size: 1.5rem;
                z-index: 10000;
                animation: fadeIn 0.5s ease;
            `;
            document.body.appendChild(message);
            
            setTimeout(() => {
                message.style.opacity = '0';
                message.style.transition = 'opacity 0.5s ease';
                setTimeout(() => message.remove(), 500);
            }, 3000);
            
            konamiCode = [];
        }
    });

    console.log('%c🎬 Coze2JianYing', 'font-size: 20px; font-weight: bold; color: #4a90e2;');
    console.log('%c开源 · 免费 · 安全', 'font-size: 14px; color: #50c878;');
    console.log('%c欢迎来到 Coze2JianYing！\n如果你发现任何问题，欢迎在 GitHub 上提交 Issue。', 'font-size: 12px;');
});
