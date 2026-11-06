# Fly Visuals — Website Redesign

New website design for Fly Visuals (signs, wraps & tint) — Port Richey, FL.

This is a working preview of the redesign. Every page, link, filter, the shop price calculator, the gallery and the mobile menu work as they will on the live site.

## See it

**Netlify (easiest):** In Netlify, choose *Add new site → Import an existing project*, pick this repo, leave the build command empty and the publish folder as `/`. Netlify gives you a live link.

**On your computer:** run `python3 -m http.server` in this folder and open http://localhost:8000.

## What's in here

| What | Files |
|---|---|
| Home page | `index.html` |
| Main pages | `Products`, `Shop`, `Industries`, `ServiceArea` (Locations), `Process`, `Financing`, `Gallery`, `Blog`, `About`, `Quote` |
| Product pages | 8 products × (main page + 5 cities) = 48 pages, e.g. `Commercial-Vehicle-Wraps-Port-Richey.dc.html` |
| Option pages | 40 pages, e.g. `Option-Channel-Letters.dc.html` |
| Shop | `Shop.dc.html` + 58 product pages (`Shop-*.dc.html`) |
| City pages | `City-*.dc.html` (Port Richey, St. Petersburg, Clearwater, Wesley Chapel, Tampa) |
| Industry pages | `Industry-*.dc.html` (9) |
| Shared templates | `Header`, `Footer`, `Product`, `City`, `Industry`, `Option`, `ShopProduct` |
| Photos | `_blob/` |
| Page engine | `support.js` |

Pages are built from shared templates. Change the product template once and all 48 product pages update.

## Still to fill in before launch

- Stripe checkout links for the shop ("Place Order & Pay" button)
- Snap Finance application link
- Google reviews link (rating badges)
- Real review text (home page)
- Client logos: GoPasco, Andy's Ice Cream, Jiffy Lube
- Drive times to each city (`[XX] minutes`)
- License number (footer)
- Product photos for items showing a placeholder
- About page story and team photos

## Before going live

Pages are drawn in the browser by `support.js`. That's fine for a preview, but for best SEO the live site should serve pre-built HTML with clean URLs (e.g. `/commercial-vehicle-wraps/port-richey/`) and per-page meta titles/descriptions.
