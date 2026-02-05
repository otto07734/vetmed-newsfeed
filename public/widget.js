/**
 * VetMed News Feed Widget
 * Embeddable news feed for veterinary medicine updates
 * 
 * Usage:
 *   <div id="vetmed-newsfeed"></div>
 *   <script src="https://vetmed-newsfeed.vercel.app/widget.js"></script>
 *   <script>VetMedNewsFeed.init({ target: '#vetmed-newsfeed', maxItems: 5 });</script>
 */

(function() {
  'use strict';

  const FEED_URL = 'https://vetmed-newsfeed.vercel.app/news.json';
  const CSS_URL = 'https://vetmed-newsfeed.vercel.app/widget.css';

  window.VetMedNewsFeed = {
    init: function(options) {
      options = options || {};
      const target = options.target || '#vetmed-newsfeed';
      const maxItems = options.maxItems || 6;
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
          const items = data.items.slice(0, maxItems);
          container.innerHTML = VetMedNewsFeed.render(items, data.lastUpdated);
        } else {
          container.innerHTML = '<div class="vetmed-newsfeed"><div class="vetmed-newsfeed-header">Vet Med News</div><div style="padding: 20px; text-align: center; color: #6b7280;">Unable to load news feed</div></div>';
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

    render: function(items, lastUpdated) {
      let html = '<div class="vetmed-newsfeed">';
      html += '<div class="vetmed-newsfeed-header">Vet Med News</div>';
      html += '<div class="vetmed-newsfeed-items">';

      items.forEach(function(item) {
        html += '<div class="vetmed-news-item">';
        html += '<div class="vetmed-news-title">';
        html += '<span class="vetmed-news-emoji">' + item.emoji + '</span>';
        html += item.title;
        html += '</div>';
        html += '<div class="vetmed-news-summary">' + item.summary + '</div>';
        html += '<a href="' + item.url + '" target="_blank" rel="noopener" class="vetmed-news-link">Read more</a>';
        html += '<div class="vetmed-news-meta">' + item.source + '</div>';
        html += '</div>';
      });

      html += '</div>';
      
      const updateDate = lastUpdated ? new Date(lastUpdated).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : '';
      html += '<div class="vetmed-newsfeed-footer">34 vet schools monitored · Updated ' + updateDate + '<br><a href="https://vetonitce.org" target="_blank">Powered by VetOnIt CE</a></div>';
      html += '</div>';

      return html;
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
