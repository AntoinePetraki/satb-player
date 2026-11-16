/* =========================================================
   Gregorian chant: gabc, drawn in square notation by exsurge
   ========================================================= */
const CHANT_TARGET={low:50,high:62};          // median pitch of the chant: D3 for low voices, D4 for high
let chantVoice=lsGet('satb:chantVoice')==='high'?'high':'low';
const isChant=()=>!!(score&&score.kind==='chant');
const unitWord=()=>isChant()?'Phrase':'Bar';
const rangeWord=()=>isChant()?'phrases':'bars';

/* Read a .gabc file: header fields above the %% line, notes below. St. Gall neumes (nabc) are dropped. */
function parseGabcFile(text,fallback){
  const lines=String(text).replace(/\r/g,'').split('\n');
  const cut=lines.findIndex(l=>l.trim()==='%%');
  const head=cut>=0?lines.slice(0,cut):[], body=(cut>=0?lines.slice(cut+1):lines).filter(l=>!/^\s*%/.test(l)).join('\n');
  const meta={};
  head.forEach(l=>{ if(/^\s*%/.test(l)) return; const m=/^\s*([A-Za-z-]+)\s*:\s*(.*?)\s*;?\s*$/.exec(l); if(m) meta[m[1].toLowerCase()]=m[2]; });
  let gabc=body.trim();
  if(meta['nabc-lines']) gabc=gabc.replace(/\(([^)]*)\)/g,(_,inner)=>'('+inner.split('|').filter((_,k)=>k%2===0).join('')+')');
  // a clef inside the first syllable, as in Pó(c3eh/hi), loses that syllable when drawn: give the clef its own group
  gabc=gabc.replace(/^([^\s(]+)\(((?:cb|c|f)[1-4])\s*([^)]*)\)/,(m,txt,clef,rest)=>`(${clef}) ${txt}(${rest})`);
  if(!/\([cf]b?[1-4]/.test(gabc)) throw new Error('This gabc file has no clef, so its pitches can’t be read.');
  return {title:(meta.name||fallback||'Chant').trim(),officePart:meta['office-part']||'',mode:meta.mode||'',gabc};
}

/* Turn a gabc file into the player's score: one line of notes timed in pulses (Solesmes style). */
function chantFromGabc(file){
  const ex=window.exsurge; if(!ex) throw new Error('The chant engraver could not load. Reopen the app while online once.');
  const ctxt=new ex.ChantContext();
  const sc=new ex.ChantScore(ctxt,ex.Gabc.createMappingsFromSource(ctxt,file.gabc),false);
  const raw=[], phrases=[{i:0,words:[]}], LT=ex.LyricType||{};
  for(const nt of sc.notations){
    const ly=nt.lyrics&&nt.lyrics[0]&&nt.lyrics[0].text?nt.lyrics[0]:null;
    if(ly){ const w=phrases[phrases.length-1].words, starts=ly.lyricType===LT.BeginningSyllable||ly.lyricType===LT.SingleSyllable||!w.length;
      const txt=String(ly.text).replace(/[*†]/g,'').trim(); if(txt){ if(starts) w.push(txt); else w[w.length-1]+=txt; } }
    if(nt.notes&&nt.notes.length){
      nt.notes.forEach(n=>{
        if(!n.pitch) return;
        let d=1;
        if(n.morae&&n.morae.length) d=2;                        // dot: doubled
        else if(n.episemata&&n.episemata.length) d=1.5;         // horizontal episema: lengthened
        if(n.shape===ex.NoteShape.Quilisma&&raw.length){ const p=raw[raw.length-1]; if(p.d<1.5) p.d=1.5; } // note before a quilisma is lengthened
        if(n.liquescent&&!(n.liquescent&16)&&d===1) d=0.8;      // liquescent: lighter
        raw.push({p:n.pitch.toInt(),d,idx:n.noteIndex});
      });
    } else if((ex.FullBar&&nt instanceof ex.FullBar)||(ex.DoubleBar&&nt instanceof ex.DoubleBar)){
      if(raw.length){ raw[raw.length-1].gap=1.5; phrases.push({i:raw.length,words:[]}); }
    } else if(ex.HalfBar&&nt instanceof ex.HalfBar){
      if(raw.length){ raw[raw.length-1].gap=1; phrases.push({i:raw.length,words:[]}); }
    } else if(ex.QuarterBar&&nt instanceof ex.QuarterBar){
      if(raw.length) raw[raw.length-1].gap=Math.max(raw[raw.length-1].gap||0,0.4);
    }
  }
  if(raw.length<2) throw new Error('No chant notes were found in this file.');
  const ph=phrases.filter(p=>p.i<raw.length);
  let t=0; raw.forEach(r=>{ r.t=t; t+=r.d+(r.gap||0); });
  const ps=raw.map(r=>r.p).sort((a,b)=>a-b), shift=CHANT_TARGET[chantVoice]-ps[ps.length>>1];
  const notes=raw.map(r=>({t:r.t,d:r.d,m:r.p+shift}));
  return {kind:'chant',src:file,title:file.title,composer:[file.officePart,file.mode?'Mode '+file.mode:''].filter(Boolean).join(' · '),
    gabc:file.gabc,raw,tempo:150,beatsPerBar:4,measures:ph.map(p=>raw[p.i].t),
    phraseLabels:ph.map((p,k)=>`${k+1} · ${p.words.slice(0,3).join(' ')||'…'}`),
    lines:[{label:'Chant',pi:0,partName:'Chant',solo:true,voice:'S',notes,avg:CHANT_TARGET[chantVoice]}],end:t,xml:null};
}

/* ---------- drawing and following the chant ---------- */
const chantMap={evs:[],lit:null,ready:false,width:0};
async function renderChantSheet(){
  const my=++renderSeq, ex=window.exsurge, box=$('chantSvg');
  sheet.ready=false; chantMap.ready=false; $('playline').style.display='none'; $('osmd').hidden=true; box.hidden=false;
  if(!ex){ sheetMsg('The chant engraver could not load. The piano roll still works.'); return; }
  sheetMsg('Engraving the chant…');
  try{
    const w=$('paper').clientWidth-28; chantMap.width=$('paper').clientWidth;
    const ctxt=new ex.ChantContext();
    if(ctxt.setStaffHeight) ctxt.setStaffHeight(w<440?30:36);
    ctxt.setFont("Georgia, 'Times New Roman', serif",w<440?15:17);
    ctxt.dropCapTextFont=ctxt.lyricTextFont; ctxt.annotationTextFont=ctxt.lyricTextFont;
    if(ex.TextMeasuringStrategy) ctxt.textMeasuringStrategy=ex.TextMeasuringStrategy.Canvas;
    const sc=new ex.ChantScore(ctxt,ex.Gabc.createMappingsFromSource(ctxt,score.gabc),true);
    await new Promise(r=>sc.performLayoutAsync(ctxt,r));
    if(my!==renderSeq) return;
    await new Promise(r=>sc.layoutChantLines(ctxt,w,r));
    if(my!==renderSeq) return;
    box.innerHTML=''; box.appendChild(sc.createSvgNode(ctxt));
    buildChantMap(ctxt.noteIdPrefix||'note-');
    sheet.stale=false; sheetMsg('');
  }catch(e){ console.error(e); if(my===renderSeq) sheetMsg('This chant could not be drawn. The piano roll still works.'); }
}
function buildChantMap(prefix){
  const pr=$('paper').getBoundingClientRect(), svg=$('chantSvg').querySelector('svg'), notes=score.lines[0].notes;
  const evs=[]; let prev=null;
  score.raw.forEach((r,k)=>{
    const el=svg.querySelector('#'+CSS.escape(prefix+(r.idx+1)));
    const g=el&&el.closest('g.chantLine'), staff=g&&g.querySelector('g.staffLines');
    let x, line=null, top, bottom;
    if(el&&staff){
      const bb=el.getBoundingClientRect(), sb=staff.getBoundingClientRect();
      x=bb.left-pr.left+Math.min(bb.width/2,6); line=g; top=sb.top-pr.top-8; bottom=sb.bottom-pr.top+8;
      top=Math.min(top,bb.top-pr.top-4); bottom=Math.max(bottom,bb.bottom-pr.top+4);
    } else if(prev){ x=prev.x+8; line=prev.line; top=prev.top; bottom=prev.bottom; }
    else return;
    const ev={k,b:notes[k].t,e:notes[k].t+notes[k].d,x,line,top,bottom,el:(el&&el.getAttribute('class')||'').includes('note')?el:null};
    evs.push(ev); prev=ev;
  });
  // the end of each line of music, for the playhead to run to before it wraps
  evs.forEach((ev,i)=>{ const nx=evs[i+1]; ev.nextX=nx&&nx.line===ev.line?nx.x:ev.x+14; ev.nextB=nx?nx.b:ev.e; });
  chantMap.evs=evs; chantMap.lit=null; chantMap.ready=true; sheet.ready=true;
  updateChantSheet(currentBeat());
}
function updateChantSheet(beat){
  const evs=chantMap.evs, line=$('playline'); if(!chantMap.ready||!evs.length) return;
  let lo=0,hi=evs.length-1; while(lo<hi){const mid=(lo+hi+1)>>1; if(evs[mid].b<=beat+1e-9) lo=mid; else hi=mid-1;}
  const ev=evs[lo], span=Math.max(1e-6,ev.nextB-ev.b), r=clamp((beat-ev.b)/span,0,1);
  const x=beat<ev.b?ev.x:ev.x+(ev.nextX-ev.x)*r;
  line.style.display='block'; line.style.height=(ev.bottom-ev.top)+'px'; line.style.transform=`translate(${x-1}px,${ev.top}px)`;
  const on=playing&&beat>=ev.b-1e-6&&beat<ev.e?ev:null;
  if(chantMap.lit!==on){ if(chantMap.lit&&chantMap.lit.el) chantMap.lit.el.classList.remove('on'); if(on&&on.el) on.el.classList.add('on'); chantMap.lit=on; }
  if(playing&&$('follow').checked){
    const key=Math.round(ev.top);
    if(key!==lastScrollKey){
      lastScrollKey=key;
      const pr=$('paper').getBoundingClientRect(), tr=document.querySelector('.transport').getBoundingClientRect();
      const top=pr.top+ev.top, bot=pr.top+ev.bottom+30, room=tr.top-12;
      if(top<12||bot>room) window.scrollTo({top:Math.max(0,window.scrollY+top-Math.min(90,room*0.15)),behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});
    }
  }
}
function chantClick(e){
  if(!chantMap.ready) return;
  const r=$('paper').getBoundingClientRect(), x=e.clientX-r.left, y=e.clientY-r.top;
  let best=null,bd=1e9;
  chantMap.evs.forEach(ev=>{ if(y<ev.top-30||y>ev.bottom+40) return; const d=Math.abs(ev.x-x); if(d<bd){bd=d;best=ev;} });
  if(best&&bd<40) jumpTo(best.b);
}

/* ---------- switching between choir and chant ---------- */
function applyMode(){
  const c=isChant();
  VNAME.S=c?'Chant':'Soprano';
  if(c) sel=new Set(VOICES);
  $('voicesSec').hidden=c; $('mini').hidden=c; $('othersRow').hidden=c; $('mapBox').hidden=c; $('chantRow').hidden=!c;
  $('rangeName').textContent=c?'Phrases':'Bars'; $('rangeHint').textContent=c?'Practise one phrase or a few':'Practise one passage';
  $('countName').textContent=c?'Starting note':'Count-in'; $('loopHint').textContent=c?'Repeat the chosen phrases':'Repeat the chosen bars'; $('countHint').textContent=c?'Hear the first note before you start':'One bar of clicks before you start';
  $('osmd').hidden=c; $('chantSvg').hidden=!c;
  $('cvLow').setAttribute('aria-pressed',chantVoice==='low'); $('cvHigh').setAttribute('aria-pressed',chantVoice==='high');
}
function setChantVoice(v){
  if(v===chantVoice||!isChant()) return;
  chantVoice=v; lsSet('satb:chantVoice',v);
  const src=score.src; loadScore(chantFromGabc(src),{keepTempo:true});
}
$('cvLow').addEventListener('click',()=>setChantVoice('low'));
$('cvHigh').addEventListener('click',()=>setChantVoice('high'));
