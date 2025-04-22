odoo.define('universidad.animations', function (require) {
    'use strict';

    const Widget = require('web.Widget');
    const publicWidget = require('web.public.widget');

    const UniversityAnimations = Widget.extend({
        start: function () {
            this._initCounters();
            this._initScrollAnimations();
            return this._super.apply(this, arguments);
        },

        _initCounters: function () {
            const counters = document.querySelectorAll('.counter');
            
            counters.forEach(counter => {
                const target = parseInt(counter.getAttribute('data-target') || '0');
                let current = 0;
                
                const updateCounter = () => {
                    const increment = target / 100;
                    if (current < target) {
                        current += increment;
                        counter.textContent = Math.ceil(current);
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target;
                    }
                };
                
                updateCounter();
            });
        },

        _initScrollAnimations: function () {
            const observer = new IntersectionObserver(
                (entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('animated');
                        }
                    });
                },
                { threshold: 0.1 }
            );

            document.querySelectorAll('.stat-item, .university-card').forEach(
                element => observer.observe(element)
            );
        }
    });

    publicWidget.registry.universityAnimations = UniversityAnimations;

    return UniversityAnimations;
});