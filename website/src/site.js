const base = document.currentScript?.src ? new URL('.', document.currentScript.src) : new URL('./', window.location.href);
const contractUrl = new URL('openapi.json', base);
const list = document.querySelector('#api-reference');
const status = document.querySelector('#contract-status');
const filter = document.querySelector('#filter');
let endpoints = [];

function render() {
  const query = filter.value.trim().toLowerCase();
  const visible = endpoints.filter((item) => !query || `${item.method} ${item.path} ${item.summary}`.toLowerCase().includes(query));
  list.innerHTML = visible.map(({ method, path, operation }) => `<details class="endpoint"><summary><span class="method ${method}">${method.toUpperCase()}</span><span class="path">${path}</span><span>${operation.summary || ''}</span></summary><div class="endpoint-body"><h4>${operation.operationId || 'Endpoint'}</h4><p>${operation.description || 'No additional description.'}</p></div></details>`).join('') || '<p class="muted">No matching endpoints.</p>';
  status.textContent = `${visible.length} of ${endpoints.length} endpoints · generated from local OpenAPI JSON`;
}

fetch(contractUrl).then((response) => { if (!response.ok) throw new Error(`HTTP ${response.status}`); return response.json(); }).then((schema) => {
  endpoints = Object.entries(schema.paths || {}).flatMap(([path, operations]) => Object.entries(operations).filter(([method]) => ['get','post','put','patch','delete','options','head'].includes(method)).map(([method, operation]) => ({ method, path, operation, summary: operation.summary || '' })));
  render();
}).catch((error) => { status.textContent = `Unable to load the local OpenAPI contract: ${error.message}`; });
filter.addEventListener('input', render);
