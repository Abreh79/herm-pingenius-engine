/**
 * PinGenius Studio Client Application v2.1
 */

let currentTab = 'static';
let lastPayload = null;

function openHistoryDrawer() {
  const m = document.getElementById('historyModal');
  if (!m) { alert('Modal element missing'); return; }
  m.classList.remove('hidden');
  m.style.display = 'flex';
  m.style.zIndex = '99999';
  fetch('/api/campaigns')
    .then(r => r.json())
    .then(data => {
      const list = document.getElementById('campaignHistoryList');
      if (!list) return;
      if (!data || !data.campaigns || data.campaigns.length === 0) {
        list.innerHTML = '<p class="text-gray-400 p-4">No campaigns saved yet. Generate one first!</p>';
        return;
      }
      list.innerHTML = data.campaigns.map(c => `
        <div class="p-3 bg-gray-800 rounded border border-gray-700 mb-2 flex justify-between items-center">
          <div>
            <p class="font-bold text-white text-sm">${c.topic || 'Untitled'}</p>
            <p class="text-xs text-gray-400">${c.timestamp || ''} • ${c.niche || ''}</p>
          </div>
          <a href="/api/download?path=${encodeURIComponent(c.zip_path)}" class="px-3 py-1 bg-amber-500 hover:bg-amber-600 text-black text-xs font-bold rounded">Download ZIP</a>
        </div>
      `).join('');
    })
    .catch(err => {
      console.error(err);
      alert('Failed to load history: ' + err.message);
    });
}

function closeHistoryDrawer() {
  const m = document.getElementById('historyModal');
  if (m) { m.style.display = 'none'; m.classList.add('hidden'); }
}

function switchTab(tab) {
  currentTab = tab;
  const staticBtn = document.getElementById('tabStaticBtn');
  const carouselBtn = document.getElementById('tabCarouselBtn');
  const motionBtn = document.getElementById('tabMotionBtn');
  const staticSec = document.getElementById('staticPinsSection');
  const carouselSec = document.getElementById('carouselSection');
  const motionSec = document.getElementById('motionSection');

  [staticBtn, carouselBtn, motionBtn].forEach(btn => {
    if (btn) btn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-slate-800 text-slate-300 hover:bg-slate-700';
  });
  [staticSec, carouselSec, motionSec].forEach(sec => {
    if (sec) sec.classList.add('hidden');
  });

  if (tab === 'static') {
    if (staticBtn) staticBtn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-brand text-white shadow-md';
    if (staticSec) staticSec.classList.remove('hidden');
  } else if (tab === 'carousel') {
    if (carouselBtn) carouselBtn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-brand text-white shadow-md';
    if (carouselSec) carouselSec.classList.remove('hidden');
  } else if (tab === 'motion') {
    if (motionBtn) motionBtn.className = 'px-4 py-2 rounded-xl text-xs font-bold transition bg-brand text-white shadow-md';
    if (motionSec) motionSec.classList.remove('hidden');
  }
}

async function promptDispatch() {
  if (!lastPayload) {
    alert('No active campaign payload available to dispatch.');
    return;
  }
  const webhookUrl = prompt('Enter your Automation Webhook URL (Zapier / Make / Pabbly / Custom Endpoint):', 'https://hooks.zapier.com/hooks/catch/pingenius');
  if (!webhookUrl) return;

  try {
    const resp = await fetch('/api/dispatch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ webhook_url: webhookUrl, campaign: lastPayload })
    });
    const resData = await resp.json();
    if (resData.status === 'success') {
      alert('⚡ Campaign Dispatch Dispatched Successfully!\n' + resData.message);
    } else {
      alert('Dispatch error: ' + resData.message);
    }
  } catch (err) {
    alert('Failed to dispatch webhook: ' + err);
  }
}

async function checkAccount() {
  const apiKeyEl = document.getElementById('apiKeyInput');
  if (!apiKeyEl) return;
  const apiKey = apiKeyEl.value;
  try {
    const resp = await fetch(`/api/account?api_key=${encodeURIComponent(apiKey)}`);
    if (!resp.ok) return;
    const data = await resp.json();
    if (data.valid) {
      const creditCount = document.getElementById('creditCount');
      const tierLabel = document.getElementById('tierLabel');
      const creditBadge = document.getElementById('creditBadge');
      if (creditCount) creditCount.innerText = data.credits;
      if (tierLabel) tierLabel.innerText = `${data.tier} Tier`;
      if (creditBadge) creditBadge.classList.remove('hidden');
    }
  } catch (err) {
    console.error(err);
  }
}

function renderResults(data) {
  lastPayload = data;
  const resTitle = document.getElementById('resTitle');
  const resSub = document.getElementById('resSub');
  const downloadZip = document.getElementById('downloadZip');
  const downloadCsv = document.getElementById('downloadCsv');
  const creditCount = document.getElementById('creditCount');

  if (resTitle) resTitle.innerText = `${data.summary?.topic || ''} (${data.summary?.niche || ''})`;
  if (resSub) resSub.innerText = `Engine: ${data.summary?.ai_engine || 'PinGenius'} • 10 HD Pins + Bulk CSV Generated • Remaining Credits: ${data.credits_remaining ?? '--'}`;
  if (downloadZip) downloadZip.href = data.summary?.zip_download_url || '#';
  if (downloadCsv) downloadCsv.href = data.summary?.csv_download_url || '#';
  if (creditCount && data.credits_remaining !== undefined) creditCount.innerText = data.credits_remaining;

  const pinsGrid = document.getElementById('pinsGrid');
  if (pinsGrid) {
    pinsGrid.innerHTML = '';
    (data.pins || []).forEach(pin => {
      pinsGrid.innerHTML += `
        <div class="bg-cardbg rounded-2xl border border-slate-800 overflow-hidden shadow-xl group hover:border-brand/50 transition duration-300 flex flex-col justify-between">
          <div class="relative overflow-hidden aspect-[2/3] bg-slate-900">
            <img src="${pin.image_url}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
            <div class="absolute top-2 left-2 bg-slate-950/80 backdrop-blur px-2.5 py-1 rounded-full text-[10px] font-bold text-amber-400 border border-amber-500/20">
              Variant ${pin.variant_id}
            </div>
            <div class="absolute top-2 right-2 bg-slate-950/80 backdrop-blur px-2 py-1 rounded-full text-[9px] font-semibold text-slate-300 border border-slate-700 uppercase">
              ${pin.layout || 'standard'}
            </div>
          </div>
          <div class="p-3 bg-slate-900/90 border-t border-slate-800 flex flex-col justify-between flex-grow">
            <p class="text-xs font-semibold text-slate-200 line-clamp-2 mb-3 leading-snug">${pin.hook}</p>
            <a href="${pin.download_url}" download class="w-full bg-slate-800 hover:bg-brand text-slate-200 hover:text-white text-xs font-bold py-2 rounded-xl transition text-center flex items-center justify-center space-x-1 shadow">
              <span>Download PNG</span>
            </a>
          </div>
        </div>
      `;
    });
  }

  const carouselGrid = document.getElementById('carouselGrid');
  if (carouselGrid) {
    carouselGrid.innerHTML = '';
    (data.carousel || []).forEach(slide => {
      carouselGrid.innerHTML += `
        <div class="bg-cardbg rounded-2xl border border-slate-800 overflow-hidden shadow-xl group hover:border-brand/50 transition duration-300 flex flex-col justify-between">
          <div class="relative overflow-hidden aspect-[2/3] bg-slate-900">
            <img src="${slide.image_url}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300">
            <div class="absolute top-2 left-2 bg-brand px-2.5 py-1 rounded-full text-[10px] font-bold text-white shadow">
              Slide ${slide.slide} / 5
            </div>
          </div>
          <div class="p-3 bg-slate-900/90 border-t border-slate-800 flex flex-col justify-between flex-grow">
            <p class="text-xs font-semibold text-slate-200 line-clamp-2 mb-3 leading-snug">${slide.hook || 'Carousel Slide'}</p>
            <a href="${slide.download_url}" download class="w-full bg-slate-800 hover:bg-brand text-slate-200 hover:text-white text-xs font-bold py-2 rounded-xl transition text-center flex items-center justify-center space-x-1 shadow">
              <span>Download PNG</span>
            </a>
          </div>
        </div>
      `;
    });
  }

  const motionCard = document.getElementById('motionCard');
  if (motionCard) {
    if (data.motion_pin && data.motion_pin.video_url) {
      motionCard.innerHTML = `
        <div class="bg-cardbg rounded-2xl border border-slate-800 overflow-hidden shadow-xl p-6 flex flex-col items-center">
          <div class="relative aspect-[9/16] w-full max-w-sm rounded-xl overflow-hidden bg-slate-950 border border-slate-800 mb-4 shadow-2xl">
            <video src="${data.motion_pin.video_url}" controls autoplay loop muted playsinline class="w-full h-full object-cover"></video>
          </div>
          <h4 class="text-base font-bold text-white mb-1 text-center">${data.motion_pin.title || 'Kinetic Video Pin'}</h4>
          <p class="text-xs text-slate-400 mb-4 text-center line-clamp-2">${data.motion_pin.description || ''}</p>
          <a href="${data.motion_pin.download_url}" download class="w-full bg-brand hover:bg-red-700 text-white font-bold py-3 rounded-xl transition text-center shadow-lg shadow-brand/20 flex items-center justify-center space-x-2 text-xs">
            <span>🎥 Download MP4 Video Pin</span>
          </a>
        </div>
      `;
    } else {
      motionCard.innerHTML = '<p class="text-xs text-slate-400 text-center py-6">No motion pin generated.</p>';
    }
  }

  switchTab('static');
  const results = document.getElementById('results');
  if (results) results.classList.remove('hidden');
}

async function handleGenerate(event) {
  if (event && event.preventDefault) {
    event.preventDefault();
  }
  const topic = document.getElementById('topicInput')?.value || '';
  const niche = document.getElementById('nicheInput')?.value || '';
  const url = document.getElementById('urlInput')?.value || '';
  const apiKey = document.getElementById('apiKeyInput')?.value || 'herm_master_key_777';
  const geminiKey = document.getElementById('geminiKeyInput')?.value || '';
  const btn = document.getElementById('submitBtn') || document.getElementById('generateBtn');
  const loading = document.getElementById('loading');
  const results = document.getElementById('results');

  if (btn) {
    btn.innerText = 'Generating Campaign & MP4...';
    btn.disabled = true;
  }
  if (loading) loading.classList.remove('hidden');
  if (results) results.classList.add('hidden');

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': apiKey,
        'X-Gemini-API-Key': geminiKey
      },
      body: JSON.stringify({ topic, niche, url, api_key: apiKey, gemini_key: geminiKey })
    });
    const data = await res.json();
    if (data.status === 'success') {
      renderResults(data);
    } else {
      alert('Error: ' + (data.message || JSON.stringify(data)));
    }
  } catch (err) {
    console.error(err);
    alert('Fetch failed: ' + err.message);
  } finally {
    if (loading) loading.classList.add('hidden');
    if (btn) {
      btn.innerText = 'Generate Campaign Artwork & Bulk CSV';
      btn.disabled = false;
    }
  }
}

// Bind event handlers on DOM loaded
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('genForm');
  if (form) {
    form.addEventListener('submit', handleGenerate);
  }
  checkAccount();
});
