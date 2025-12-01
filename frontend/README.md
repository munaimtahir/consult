# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## Troubleshooting npm 403 errors

If `npm install` returns a `403` response from `registry.npmjs.org`, try the steps below:

1. **Force the public registry**
   - `npm config set registry https://registry.npmjs.org/`
2. **Clear cached proxy or token settings**
   - Remove unintended proxy config: `npm config delete proxy` and `npm config delete https-proxy`.
   - Remove stale auth tokens: `npm config delete //registry.npmjs.org/:_authToken`.
3. **Reset the cache**
   - `npm cache clean --force`
4. **Retry the install with explicit registry and no audit**
   - `npm install --registry=https://registry.npmjs.org/ --no-audit --progress=false`

If your network requires an authenticated proxy, add the correct proxy URL back with `npm config set proxy <http-proxy>` and `npm config set https-proxy <https-proxy>` after confirming the credentials work in a browser.
