(function(){
 'use strict';
 const header=document.querySelector('.site-header');
 if(header){
   const updateHeader=()=>header.classList.toggle('is-scrolled',window.scrollY>12);
   updateHeader();
   window.addEventListener('scroll',updateHeader,{passive:true});
 }
 const motionAllowed=window.matchMedia('(prefers-reduced-motion: no-preference)').matches;
 if('IntersectionObserver' in window&&motionAllowed){
   const reveals=Array.from(document.querySelectorAll('.reveal'));
   ['.features-grid .feature','.news-grid .news-card','.mandate-cards .mandate-card','.doc-grid .doc-tile'].forEach(selector=>{
     document.querySelectorAll(selector).forEach((element,index)=>element.style.setProperty('--reveal-delay',`${index*110}ms`));
   });
   document.documentElement.classList.add('js-reveal');
   const revealObserver=new IntersectionObserver(entries=>{
     entries.forEach(entry=>{
       entry.target.classList.toggle('is-visible',entry.isIntersecting);
     });
   },{threshold:0,rootMargin:'0px 0px -70px 0px'});
   reveals.forEach(element=>revealObserver.observe(element));
 }
 const menuButton=document.querySelector('.nav-toggle');
 const nav=document.querySelector('.site-nav');
 if(menuButton&&nav){
   menuButton.addEventListener('click',function(){const open=menuButton.getAttribute('aria-expanded')==='true';menuButton.setAttribute('aria-expanded',String(!open));menuButton.setAttribute('aria-label',open?'Ouvrir le menu':'Fermer le menu');nav.classList.toggle('is-open',!open);});
   nav.querySelectorAll('a').forEach(a=>a.addEventListener('click',function(){menuButton.setAttribute('aria-expanded','false');nav.classList.remove('is-open');}));
 }
 const filterButtons=Array.from(document.querySelectorAll('[data-filter]'));
 const newsCards=Array.from(document.querySelectorAll('.news-card'));
 filterButtons.forEach(button=>button.addEventListener('click',function(){const category=button.dataset.filter;filterButtons.forEach(b=>{const active=b===button;b.classList.toggle('is-active',active);b.setAttribute('aria-pressed',String(active));});newsCards.forEach(card=>{card.classList.toggle('is-hidden',category!=='tous'&&card.dataset.category!==category);});}));
 const modal=document.getElementById('readerModal');
 const open=document.getElementById('openReader');
 const previewOpen=document.getElementById('openReaderPreview');
 const close=document.getElementById('closeReader');
 const img=document.getElementById('readerImage');
 const counter=document.getElementById('readerCount');
 const prev=document.getElementById('readerPrev');
 const next=document.getElementById('readerNext');
 const dots=Array.from(document.querySelectorAll('#readerDots [data-page]'));
 let activePage=1,lastFocus=null;
 function goToPage(n){const page=Math.min(4,Math.max(1,n));const direction=page>activePage?'next':'prev';const changed=page!==activePage;activePage=page;img.src='assets/lettre/lettre-page-'+activePage+'.webp';img.alt='Page '+activePage+' de la lettre mensuelle type';if(changed&&motionAllowed){img.classList.remove('page-turn-next','page-turn-prev');void img.offsetWidth;img.classList.add('page-turn-'+direction);}counter.textContent='Page '+activePage+' / 4';prev.disabled=activePage===1;next.disabled=activePage===4;dots.forEach((b,i)=>{b.classList.toggle('is-active',i+1===activePage);b.setAttribute('aria-current',String(i+1===activePage));});}
 function openModal(){lastFocus=document.activeElement;modal.hidden=false;document.body.classList.add('reader-open');for(let page=2;page<=4;page++){const preload=new Image();preload.src='assets/lettre/lettre-page-'+page+'.webp';}goToPage(1);close.focus();}
 function closeModal(){modal.hidden=true;document.body.classList.remove('reader-open');if(lastFocus&&typeof lastFocus.focus==='function')lastFocus.focus();}
 if(open&&modal){open.addEventListener('click',openModal);previewOpen.addEventListener('click',openModal);close.addEventListener('click',closeModal);document.querySelectorAll('[data-close-reader]').forEach(el=>el.addEventListener('click',closeModal));prev.addEventListener('click',()=>goToPage(activePage-1));next.addEventListener('click',()=>goToPage(activePage+1));dots.forEach(b=>b.addEventListener('click',()=>goToPage(Number(b.dataset.page))));document.addEventListener('keydown',function(e){if(modal.hidden)return;if(e.key==='Escape'){closeModal();}if(e.key==='ArrowLeft'){goToPage(activePage-1);}if(e.key==='ArrowRight'){goToPage(activePage+1);}if(e.key==='Tab'){const all=[...modal.querySelectorAll('a[href],button:not([disabled])')].filter(x=>x.offsetParent!==null);if(!all.length)return;const first=all[0],last=all[all.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}});}
})();
