/**
 * VetMed News Feed Widget
 * Embeddable news feed for veterinary medicine updates
 * 
 * Usage:
 *   <div id="vetmed-newsfeed"></div>
 *   <script src="https://vetmed-newsfeed.vercel.app/widget.js"></script>
 *   <script>VetMedNewsFeed.init({ target: '#vetmed-newsfeed' });</script>
 */

(function() {
  'use strict';

  const FEED_URL = 'https://vetmed-newsfeed.vercel.app/news.json';
  const CSS_URL = 'https://vetmed-newsfeed.vercel.app/widget.css';

  window.VetMedNewsFeed = {
    init: function(options) {
      options = options || {};
      const target = options.target || '#vetmed-newsfeed';
      const height = options.height || 500;
      const container = document.querySelector(target);

      if (!container) {
        console.error('VetMedNewsFeed: Target element not found:', target);
        return;
      }

      // Load CSS
      if (!document.querySelector('link[href*="widget.css"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = CSS_URL;
        document.head.appendChild(link);
      }

      // Fetch and render
      this.fetchNews(function(data) {
        if (data && data.items) {
          container.innerHTML = VetMedNewsFeed.render(data.items, data.lastUpdated, height);
          VetMedNewsFeed.initInfiniteScroll(container);
        } else {
          container.innerHTML = '<div class="vetmed-newsfeed"><div class="vetmed-newsfeed-header">Vet On It CE: Vet Med News and Research Feed</div><div style="padding: 20px; text-align: center; color: #6b7280;">Unable to load news feed</div></div>';
        }
      });
    },

    fetchNews: function(callback) {
      fetch(FEED_URL)
        .then(function(response) {
          return response.json();
        })
        .then(callback)
        .catch(function(err) {
          console.error('VetMedNewsFeed: Error fetching news:', err);
          callback(null);
        });
    },

    render: function(items, lastUpdated, height) {
      let html = '<div class="vetmed-newsfeed">';
      html += '<div class="vetmed-newsfeed-header">Vet On It CE: Vet Med News and Research Feed</div>';
      html += '<div class="vetmed-newsfeed-items" style="max-height: ' + height + 'px;" data-item-count="' + items.length + '">';

      // Render all items
      items.forEach(function(item, index) {
        html += VetMedNewsFeed.renderItem(item, index);
      });

      html += '</div>';
      
      const updateDate = lastUpdated ? new Date(lastUpdated).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '';
      html += '<div class="vetmed-newsfeed-footer">';
      html += '<div class="vetmed-scroll-hint">↓ Scroll for more • ' + items.length + ' articles</div>';
      html += '34 vet schools monitored · Updated ' + updateDate + '<br><a href="https://vetonitce.org" target="_blank">Powered by VetOnIt CE</a>';
      html += '</div>';
      html += '</div>';

      return html;
    },

    renderItem: function(item, index) {
      let html = '<div class="vetmed-news-item" data-index="' + index + '">';
      html += '<div class="vetmed-news-title">';
      html += '<span class="vetmed-news-emoji">' + item.emoji + '</span>';
      html += item.title;
      html += '</div>';
      html += '<div class="vetmed-news-summary">' + item.summary + '</div>';
      html += '<a href="' + item.url + '" target="_blank" rel="noopener" class="vetmed-news-link">Read more</a>';
      html += '<div class="vetmed-news-meta">' + item.source + '</div>';
      html += '</div>';
      return html;
    },

    initInfiniteScroll: function(container) {
      const scrollContainer = container.querySelector('.vetmed-newsfeed-items');
      const scrollHint = container.querySelector('.vetmed-scroll-hint');
      if (!scrollContainer) return;

      const itemCount = parseInt(scrollContainer.dataset.itemCount, 10);
      let loopCount = 0;
      const maxLoops = 10; // Prevent infinite memory growth

      scrollContainer.addEventListener('scroll', function() {
        const scrollTop = scrollContainer.scrollTop;
        const scrollHeight = scrollContainer.scrollHeight;
        const clientHeight = scrollContainer.clientHeight;
        
        // Update scroll hint
        if (scrollHint) {
          if (scrollTop > 50) {
            scrollHint.textContent = '↑↓ Scroll • ' + itemCount + ' articles (loops at end)';
          } else {
            scrollHint.textContent = '↓ Scroll for more • ' + itemCount + ' articles';
          }
        }

        // Check if near bottom (within 100px)
        if (scrollTop + clientHeight >= scrollHeight - 100 && loopCount < maxLoops) {
          loopCount++;
          // Clone and append all items for infinite scroll effect
          const items = scrollContainer.querySelectorAll('.vetmed-news-item');
          const originalItems = Array.from(items).slice(0, itemCount);
          
          originalItems.forEach(function(item, index) {
            const clone = item.cloneNode(true);
            clone.dataset.index = itemCount * loopCount + index;
            scrollContainer.appendChild(clone);
          });

          if (scrollHint) {
            scrollHint.textContent = '↻ Looped • ' + itemCount + ' articles';
          }
        }
      });
    }
  };

  // Auto-init if target exists
  document.addEventListener('DOMContentLoaded', function() {
    const autoTarget = document.querySelector('#vetmed-newsfeed');
    if (autoTarget && !autoTarget.hasAttribute('data-manual')) {
      VetMedNewsFeed.init();
    }
  });
})();
