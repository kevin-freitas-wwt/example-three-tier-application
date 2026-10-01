# Riverside Burger Co. — Restaurant Homepage

A simple, static homepage for a neighborhood burger restaurant. It's plain HTML, CSS, and JavaScript — no build step, no framework, no compiled tech. It is independent of the Next.js app in `src/web/`.

## View it

Open `index.html` directly in a browser, or serve the folder with any static file server, e.g.:

```bash
npx serve restaurant
```

## Files

- `index.html` — page structure
- `styles.css` — styling, including automatic light/dark mode via `prefers-color-scheme`
- `script.js` — renders the menu and hours, and shows a live open/closed status based on the current time
