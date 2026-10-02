# Python targets with Vue presentation

Service problems keep target logic in `vulnerable/app.py` and presentation in
`vulnerable/web/App.vue`. Python owns routes, input processing, session cookies,
authorization and the intended vulnerable or patched policy. Vue displays only
data returned by those routes. Private records and generated flags stay on the
server until the exercise grants access to them.

The repository's `web` directory owns Vite configuration, Vue bootstrapping,
HTTP asset serving, shared page styles, error/loading treatment and bundled
Pretendard Variable 1.3.9. Problem components import these presentation helpers;
the platform repository is unnecessary for authoring, checking or building them.

## HTTP and navigation

Browser document requests accepting `text/html` receive the built Vue document.
The component reads the same path with `Accept: application/json`; page data is
JSON and exercise text endpoints retain their text response. Existing API paths,
query parameters, cookies, generated flags and policy decisions stay in Python.
Native links and GET forms perform normal document navigation, retaining URL
editing, browser history and the platform's common browsing tools.

`web.server.TargetHandler` confines static reads to the built `assets` directory,
sets MIME types and provides JSON/document responses. Each target opts its own
routes into presentation; the helper does not decide target authorization.
Vue text interpolation preserves escaping for these current exercises. Future
rendering vulnerabilities must explicitly author and verify their required
rendering behavior rather than assuming ordinary escaped interpolation exposes
HTML execution.

## Build and checks

The problem's Dockerfile builds its Vue component with Node 24.21.0, pnpm 12.8.1,
Vue 3.5.43, Vite 8.3.1 and the pinned TypeScript native bridge. Direct dependencies
use exact versions and the frozen lockfile. The runtime image contains Python
and built local assets. It uses the existing non-root, read-only, isolated
configuration. Running targets requires no Node process, CDN or external font
request.

Build contexts stay within the challenges repository. `tools/create.py` writes
the service component and build wiring, using this shared `web` source. Build
output and dependencies are ignored; they are rebuilt from the committed sources.

Check types and rendered behavior using Docker alone:

```sh
docker build --file web/Dockerfile --target check .
python3 -B -m unittest discover -s tools -p 'test_*.py'
python3 -B tools/validate.py
python3 -B tools/verify.py
```

CI and committed-snapshot publication run the Vue check. Rendering tests cover
note lists and escaped bodies, search forms and escaped rows, history links,
cookie editing, file lookup and archive clues. Python tests cover static path
containment and representation negotiation. Actual Docker verification checks
every service's normal use, intended solution, patched denial and cleanup.
