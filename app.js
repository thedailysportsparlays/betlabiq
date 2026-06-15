const picksGrid = document.querySelector('#picksGrid');
const filters = document.querySelectorAll('.filter');
const pickCount = document.querySelector('#pickCount');
const avgEdge = document.querySelector('#avgEdge');
const heroConfidence = document.querySelector('#heroConfidence');
let allPicks = [];

function formatEdge(edge){
  const n = Number(edge || 0);
  return `${n > 0 ? '+' : ''}${n.toFixed(1)}%`;
}

function card(p){
  const premium = p.is_premium ? '<span class="premium-lock">Premium</span>' : '<span>Free</span>';
  return `
    <article class="pick-card" data-sport="${p.sport}">
      <div class="pick-meta"><span>${p.sport} • ${p.market}</span>${premium}</div>
      <h3>${p.matchup}</h3>
      <div class="pick-main">${p.pick}</div>
      <div class="metrics">
        <div class="metric"><strong>${p.confidence}%</strong><small>Confidence</small></div>
        <div class="metric"><strong>${formatEdge(p.edge)}</strong><small>Model Edge</small></div>
        <div class="metric"><strong>${p.odds}</strong><small>Odds</small></div>
      </div>
      <div class="pick-meta"><span class="tier ${p.tier}">${p.tier}</span><span>${p.start_time}</span></div>
      <p class="reason">${p.reason_1} • ${p.reason_2} • ${p.reason_3}</p>
    </article>`;
}

function render(filter='all'){
  const picks = filter === 'all' ? allPicks : allPicks.filter(p => p.sport === filter);
  picksGrid.innerHTML = picks.length ? picks.map(card).join('') : '<p class="reason">No picks loaded for this filter yet.</p>';
}

function updateHero(){
  if(!allPicks.length) return;
  pickCount.textContent = allPicks.length;
  const edge = allPicks.reduce((sum,p)=>sum+Number(p.edge || 0),0)/allPicks.length;
  avgEdge.textContent = formatEdge(edge);
  const top = Math.max(...allPicks.map(p=>Number(p.confidence || 0)));
  heroConfidence.textContent = `${top}%`;
}

async function loadPicks(){
  try{
    const res = await fetch('todays_picks.json', {cache:'no-store'});
    allPicks = await res.json();
    updateHero();
    render();
  }catch(err){
    picksGrid.innerHTML = '<p class="reason">Prediction data could not be loaded. Check data/todays_picks.json.</p>';
    console.error(err);
  }
}

filters.forEach(btn => btn.addEventListener('click', () => {
  filters.forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  render(btn.dataset.filter);
}));

loadPicks();
