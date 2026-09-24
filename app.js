const steps=[
  ['z = W<sub>enc</sub> s','Encode what light transport needs','A non-negative linear encoder compresses each spectrum to six channels. Linearity preserves scaling and addition exactly; training makes channel-wise multiplication approximate the corresponding spectral operation.'],
  ['[z₁ z₂ z₃]  /  [z₄ z₅ z₆]','Let the RGB renderer process the code','The six latent channels are split into two RGB triplets. Existing shading and light-transport operations process these triplets in two ordinary passes, without changes inside the renderer.'],
  ['ŝ = W<sub>dec</sub> z','Recover spectral information','A well-trained linear decoder merges the six rendering channels and decodes them, before converting them for colour display. Lightweight upsamplers can bring legacy RGB assets into the same latent space.']
];
const tabs=[...document.querySelectorAll('[data-step]')];
function selectStep(i){tabs.forEach((button,j)=>{button.setAttribute('aria-selected',j===i);button.tabIndex=j===i?0:-1});document.querySelector('#formula').innerHTML=steps[i][0];document.querySelector('#step-title').textContent=steps[i][1];document.querySelector('#step-copy').textContent=steps[i][2];document.querySelector('#step-panel').setAttribute('aria-labelledby',`step-${i}`)}
tabs.forEach((button,i)=>{button.addEventListener('click',()=>selectStep(i));button.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(i+1)%tabs.length;if(event.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;if(event.key==='Home')next=0;if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();selectStep(next);tabs[next].focus()}})});

const materials=[
  {key:'glass-og550',title:'Coloured glass',detail:'OG550 · surface transmittance',metric:'Mean ΔE₂₀₀₀: 1.28 codec / 10.52 RGB',description:'A sharp spectral cutoff in Schott glass is difficult to preserve after an early RGB collapse.'},
  {key:'gold',format:'png',title:'Gold conductor',detail:'Measured metal · D65',metric:'Mean ΔE₂₀₀₀: 0.65 codec / 8.98 RGB',description:'The spectral Fresnel response preserves the hue and intensity of metallic reflection.'},
  {key:'sss-wine',title:'Subsurface scattering',detail:'Wine · homogeneous medium',metric:'Mean ΔE₂₀₀₀: 2.19 codec / 14.39 RGB',description:'Absorption and scattering travel through the renderer as encoded per-channel volume parameters.'},
  {key:'sss-hand',format:'png',title:'Heterogeneous volume',detail:'Per-voxel spectral hand',metric:'Mean ΔE₂₀₀₀: 0.93 codec / 4.00 RGB',description:'Spatially varying skin features, including freckles, knuckles and veins, remain distinguishable.'}
];
const engines=[
  {key:'blender',title:'Blender Cycles',detail:'Broadband coloured lights',description:'Open-source path tracing under broadband illumination.'},
  {key:'keyshot',title:'KeyShot',detail:'Environment-map lighting',description:'Product visualisation under a spectral environment map.'},
  {key:'maya',title:'Maya Arnold',detail:'Structured light · light 2',description:'Offline production rendering with spectrally structured illumination.'},
  {key:'unreal',title:'Unreal Engine 5',detail:'Lumen · lighting 1',description:'A real-time pipeline with Lumen global illumination.'}
];
const labels={rgb:'RGB baseline',gt:'Spectral reference',codec:'Codec · spectral assets',ours:'Full RGB-asset route',latent:'Our codec',spectral_gt:'Spectral reference'};
function comparisonCard(item,type){const engine=type==='engine';const startLeft=engine?'codec':'latent';const format=item.format||'webp';const leftChoices=engine?[['codec',labels.codec],['ours',labels.ours]]:[];const rightChoices=[['rgb',labels.rgb],['gt',labels.gt]];return `<article class="comparison-card" data-key="${item.key}" data-format="${format}"><div class="card-top"><div><span class="eyebrow">${item.detail}</span><h3>${item.title}</h3></div><span class="card-index">${engine?'RENDERER':'MATERIAL'}</span></div><p>${item.description}</p>${engine?`<div class="card-controls"><span>Show</span><div class="segmented" role="group" aria-label="${item.title} method">${leftChoices.map(([value,label],i)=>`<button type="button" data-side="left" data-value="${value}" aria-pressed="${i===0}">${label}</button>`).join('')}</div></div>`:''}<div class="card-controls"><span>Compare with</span><div class="segmented" role="group" aria-label="${item.title} comparison">${rightChoices.map(([value,label],i)=>`<button type="button" data-side="right" data-value="${value}" aria-pressed="${i===0}">${label}</button>`).join('')}</div></div><div class="comparison mini-comparison" style="--split:50%"><img class="compare-base" src="assets/${item.key}-rgb.${format}" alt="${item.title}: RGB baseline" loading="lazy"><img class="overlay compare-overlay" src="assets/${item.key}-${startLeft}.${format}" alt="${item.title}: ${labels[startLeft]}" loading="lazy"><div class="divider"><span>↔</span></div><span class="image-label left compare-left-label">${labels[startLeft]}</span><span class="image-label right compare-right-label">RGB baseline</span><input type="range" min="0" max="100" value="50" aria-label="Move the divider in the ${item.title} comparison"></div>${item.metric?`<p class="card-metric">${item.metric}</p>`:''}</article>`}
document.querySelector('#material-gallery').innerHTML=materials.map(item=>comparisonCard(item,'material')).join('');
document.querySelector('#engine-gallery').innerHTML=engines.map(item=>comparisonCard(item,'engine')).join('');
const enginePresentation={
  blender:{ratio:'1 / 1',caption:'Broadband light spectra'},
  maya:{ratio:'16 / 9',caption:'Structured light spectrum'},
  keyshot:{ratio:'4 / 3',caption:'Environment illumination'},
  unreal:{ratio:'16 / 9',caption:'Scene light spectra'}
};
document.querySelectorAll('#engine-gallery .comparison-card').forEach(card=>{
  const {ratio,caption}=enginePresentation[card.dataset.key];
  card.querySelector('.mini-comparison').style.setProperty('--image-ratio',ratio);
  const lighting=document.createElement('figure');
  lighting.className='lighting-reference';
  lighting.innerHTML=`<figcaption><span class="eyebrow">Illumination</span><span>${caption}</span></figcaption><a href="assets/${card.dataset.key}-illumination.webp" target="_blank" rel="noopener" aria-label="View ${caption.toLowerCase()}"><img src="assets/${card.dataset.key}-illumination.webp" alt="${caption}" loading="lazy"></a>`;
  card.insertBefore(lighting,card.querySelector('.card-controls'));
});
document.querySelectorAll('.comparison input[type="range"]').forEach(range=>range.addEventListener('input',()=>range.closest('.comparison').style.setProperty('--split',`${range.value}%`)));
const teaserImages={main:{rgb:'teaser-rgb.png',spectral_gt:'teaser-spectral-gt.png'},video:{rgb:'video-teaser-rgb.png',spectral_gt:'video-teaser-spectral-gt.png'}};
document.querySelectorAll('[data-teaser-group]').forEach(panel=>{const group=panel.dataset.teaserGroup;panel.querySelectorAll('[data-comparison]').forEach(button=>button.addEventListener('click',()=>{panel.querySelectorAll('[data-comparison]').forEach(other=>{const active=other===button;other.classList.toggle('selected',active);other.setAttribute('aria-pressed',active)});const value=button.dataset.comparison;const image=panel.querySelector('.compare-base');image.src=`assets/${teaserImages[group][value]}`;image.alt=`${group==='main'?'Final paper teaser':'Video teaser frame'}: ${labels[value]}`;panel.querySelector('.compare-right-label').textContent=labels[value]}))});
document.querySelectorAll('.comparison-card .segmented button').forEach(button=>button.addEventListener('click',()=>{const card=button.closest('.comparison-card');const side=button.dataset.side;card.querySelectorAll(`[data-side="${side}"]`).forEach(other=>other.setAttribute('aria-pressed',other===button));const value=button.dataset.value;const image=card.querySelector(side==='left'?'.compare-overlay':'.compare-base');image.src=`assets/${card.dataset.key}-${value}.${card.dataset.format}`;image.alt=`${card.querySelector('h3').textContent}: ${labels[value]}`;card.querySelector(side==='left'?'.compare-left-label':'.compare-right-label').textContent=labels[value]}));

const GA_MEASUREMENT_ID='G-FY8S9G6L87';
const ANALYTICS_CONSENT_KEY='spectral-codes-analytics-consent';
const cookieBanner=document.querySelector('#cookie-banner');
let analyticsLoaded=false;
function readAnalyticsConsent(){try{return localStorage.getItem(ANALYTICS_CONSENT_KEY)}catch{return null}}
function writeAnalyticsConsent(value){try{localStorage.setItem(ANALYTICS_CONSENT_KEY,value)}catch{}}
function loadAnalytics(){if(analyticsLoaded)return;analyticsLoaded=true;window.dataLayer=window.dataLayer||[];window.gtag=function(){window.dataLayer.push(arguments)};window.gtag('consent','default',{analytics_storage:'granted',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'});window.gtag('js',new Date());window.gtag('config',GA_MEASUREMENT_ID,{anonymize_ip:true});const script=document.createElement('script');script.async=true;script.src=`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;document.head.appendChild(script)}
function clearAnalyticsCookies(){document.cookie.split(';').map(cookie=>cookie.split('=')[0].trim()).filter(name=>name==='_ga'||name.startsWith('_ga_')).forEach(name=>{document.cookie=`${name}=; Max-Age=0; path=/; SameSite=Lax`})}
function setAnalyticsConsent(value){writeAnalyticsConsent(value);if(value==='granted')loadAnalytics();else{if(window.gtag)window.gtag('consent','update',{analytics_storage:'denied'});clearAnalyticsCookies()}cookieBanner.hidden=true}
document.querySelectorAll('[data-cookie-choice]').forEach(button=>button.addEventListener('click',()=>setAnalyticsConsent(button.dataset.cookieChoice)));
document.querySelector('#cookie-settings').addEventListener('click',()=>{cookieBanner.hidden=false;cookieBanner.querySelector('button').focus()});
if(readAnalyticsConsent()==='granted')loadAnalytics();else if(readAnalyticsConsent()!=='denied')cookieBanner.hidden=false;
