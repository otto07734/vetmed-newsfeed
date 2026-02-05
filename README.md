# 🐾 VetMed News Feed Widget

Embeddable news feed widget displaying veterinary medicine news from 34 schools.

## Quick Start

Add this to your website:

```html
<!-- VetMed News Feed Widget -->
<div id="vetmed-newsfeed"></div>
<script src="https://vetmed-newsfeed.vercel.app/widget.js"></script>
```

## Options

```html
<div id="my-feed"></div>
<script src="https://vetmed-newsfeed.vercel.app/widget.js"></script>
<script>
  VetMedNewsFeed.init({
    target: '#my-feed',  // CSS selector for container
    maxItems: 5          // Number of items to show (default: 6)
  });
</script>
```

## Features

- ✅ Responsive design
- ✅ Dark mode support
- ✅ Auto-updates
- ✅ Lightweight (<5KB)
- ✅ No dependencies
- ✅ CORS enabled

## Data Source

News is aggregated from 34 veterinary schools including:
- UC Davis, Cornell, Texas A&M, Penn, Tufts
- Colorado State, Florida, Georgia, NC State, Ohio State
- And 24 more programs

## API

The news feed data is available at:
```
GET https://vetmed-newsfeed.vercel.app/news.json
```

## Development

```bash
# Preview locally
npx serve public

# Deploy to Vercel
vercel
```

## License

MIT - Powered by [VetOnIt CE](https://vetonitce.org)
