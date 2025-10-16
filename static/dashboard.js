const statusEl=document.getElementById('status');
const summaryEl=document.getElementById('summary');
const metricsEl=document.getElementById('metrics');
const params=new URLSearchParams(location.search);
const authToken=params.get('token');
const authHeaders=authToken?{Authorization:`Bearer ${authToken}`}:{};
if(!authToken){summaryEl.textContent='Token required (?token=...)';}
async function fetchSummary(){try{const res=await fetch('/metrics/summary',{headers:authHeaders});if(!res.ok)throw new Error(await res.text());const data=await res.json();summaryEl.textContent=`Turns (15m): ${data.turns_15m ?? '?'} | Mean latency: ${(data.latency_mean ?? 0).toFixed(2)}s | Clients: ${data.clients ?? 0}`;}catch(err){summaryEl.textContent=`Summary unavailable: ${err.message}`;}}
function connect(){const proto=location.protocol==='https:'?'wss':'ws';const tokenParam=authToken?`?token=${encodeURIComponent(authToken)}`:'';const ws=new WebSocket(`${proto}://${location.host}/ws/metrics${tokenParam}`);ws.onopen=()=>{statusEl.textContent='Connected';};ws.onmessage=e=>{try{const data=JSON.parse(e.data);const pre=document.createElement('pre');pre.textContent=JSON.stringify(data,null,2);metricsEl.prepend(pre);while(metricsEl.childElementCount>50){metricsEl.lastChild.remove();}}catch(err){console.error('Invalid metrics payload',err);}};ws.onclose=()=>{statusEl.textContent='Disconnected. Reconnecting…';setTimeout(connect,3000);};}
if(authToken){connect();fetchSummary();setInterval(fetchSummary,60000);}
