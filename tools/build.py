"""Builds the installable app (index.html) from the Claude player page."""
import re, sys
src=open('/home/claude/satb-player.html').read()
s=src
def rep(a,b,count=1):
    global s
    assert a in s, 'missing: '+a[:80]
    s=s.replace(a,b,count)
def cut(start,end,keep_end=True,repl=''):
    """remove from start marker up to end marker"""
    global s
    i=s.index(start); j=s.index(end,i)
    s=s[:i]+repl+(s[j:] if keep_end else s[j+len(end):])

# ---------- head ----------
style_start=s.index('<style>')
head='''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>SATB Part Player</title>
<meta name="description" content="Choir rehearsal player: follow the score, play any SATB voice at any tempo, and get coached on your singing.">
<meta name="theme-color" content="#EFF0F5" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#11131D" media="(prefers-color-scheme: dark)">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="SATB Player">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<style>
@font-face{font-family:"Young Serif";src:url(fonts/young-serif-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Figtree";src:url(fonts/figtree-latin-400-normal.woff2) format("woff2");font-weight:400;font-display:swap}
@font-face{font-family:"Figtree";src:url(fonts/figtree-latin-500-normal.woff2) format("woff2");font-weight:500;font-display:swap}
@font-face{font-family:"Figtree";src:url(fonts/figtree-latin-600-normal.woff2) format("woff2");font-weight:600;font-display:swap}
@font-face{font-family:"Figtree";src:url(fonts/figtree-latin-700-normal.woff2) format("woff2");font-weight:700;font-display:swap}
:root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
html{-webkit-text-size-adjust:100%;background:#EFF0F5}
body{margin:0}
img{max-width:100%}
[hidden]{display:none!important}
</style>
'''
s=head+s[style_start:]
rep('</style>\n','</style>\n</head>\n<body>\n',1)
# the dark html background behind the safe area
rep('body{background:var(--bg);','html{background:var(--bg)}\nbody{background:var(--bg);')
# sticky transport sits above the home indicator: the root already pads the bottom
rep("padding:10px 8px calc(10px + env(safe-area-inset-bottom, 0px))}","padding:10px 8px 10px}")

# ---------- open-score row: no PDF/photo reading in the app ----------
rep('<input id="file" type="file" accept=".pdf,image/jpeg,image/png,image/webp,.musicxml,.xml,.mxl" multiple hidden>','<input id="file" type="file" accept=".musicxml,.xml,.mxl,application/vnd.recordare.musicxml+xml,application/vnd.recordare.musicxml" hidden>')
rep('PDF, photos of the pages, or MusicXML (.musicxml, .mxl). Claude reads PDFs and photos for you, about a minute per page.',
    'Opens MusicXML files (.musicxml, .mxl). For a new piece as a PDF or photos, send it to Claude in your chat and it will be added to the app.')
rep('''      Save to library
    </button>''','''      Save to library
    </button>
    <button class="btn" id="delLib" hidden>Remove from library</button>''')
rep('''      <option value="old100">Old Hundredth · hymn</option>''','''      <option value="hymne">Hymne à la nuit · Rameau</option>
      <option value="old100">Old Hundredth · hymn</option>''')
cut('  <section class="scan" id="scan" hidden>','  <section class="viewbar">')

# ---------- coach: live singing ----------
rep('<p class="coach-sub">Record yourself singing one part and upload it. You get your pitch line drawn over the written notes, scores for right notes, intonation and rhythm, and what to work on.</p>',
    '<p class="coach-sub">Sing your part live into the microphone, or upload a recording. You see your pitch against the notes, get scores for right notes, intonation and rhythm, and what to work on.</p>')
rep('''      <ol>
        <li>Pick your part, the bars and a tempo in the controls above. Slower is fine; the coach measures you at that tempo.</li>''','''      <ol>
        <li>Pick your part, the bars and a tempo in the controls above. Slower is fine; the coach measures you at that tempo.</li>
        <li>For live singing, wear headphones so the microphone hears only you. Without headphones, turn your own part off in “Voices to hear”. Tap <b>Sing live</b>, allow the microphone, and sing along: your pitch shows in the strip above the play button, and your results appear when the passage ends or you tap pause.</li>''')
rep('''        <li>Easiest setup: play this page on a computer or tablet and record with your phone’s voice recorder. Start recording a few seconds before you press play.</li>
        <li>Use headphones, or turn every voice off: the red line still moves through the score in time, so you can sing unaccompanied and keep the beat. The recording should hold only your voice.</li>
        <li>Upload the recording here. The coach finds where you start on its own.</li>''','''        <li>To use a recording instead, record yourself singing the same bars (only your voice on it) and tap <b>Upload recording</b>. The coach finds where you start on its own.</li>''')
rep('''      <label class="btn primary" for="recFile">''','''      <button class="btn primary" id="liveBtn">
        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg>
        <span id="liveLabel">Sing live</span>
      </button>
      <label class="btn" for="recFile">''')
rep('''        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3zm5-3a5 5 0 0 1-10 0H5a7 7 0 0 0 6 6.92V21h2v-3.08A7 7 0 0 0 19 11h-2z"/></svg>
        Upload recording''','''        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 3l5 5h-3v6h-4V8H7l5-5zM5 18h14v2H5z"/></svg>
        Upload recording''')
# remove "coaching from Claude"
cut('        <div class="ask" id="askBox" hidden>','      </div>\n    </div>\n  </section>')
s=s.replace('''        <ul class="worst" id="worst"></ul>
      </div>
    </div>
  </section>''','''        <ul class="worst" id="worst"></ul>
      </div>
    </div>
  </section>''')
# live pitch strip inside the sticky transport
rep('''  <section class="transport">''','''  <section class="transport">
    <div class="livestrip" id="liveStrip" hidden>
      <canvas id="liveCv" aria-label="Your live pitch against the notes of your part"></canvas>
      <div class="liveinfo"><span id="liveWant"></span><span id="liveGot">Listening…</span></div>
    </div>''')
rep('.spacer{height:24px}','''.spacer{height:24px}
.livestrip{flex:1 1 100%;display:flex;flex-direction:column;gap:4px;min-width:0}
#liveCv{height:92px;border-radius:10px;background:var(--surface);border:1px solid var(--line);cursor:default}
.liveinfo{display:flex;justify-content:space-between;gap:12px;font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.liveinfo b{color:var(--ink);font-weight:600}''')

# ---------- scripts: local copies, no Claude ----------
s=re.sub(r'<script type="text/plain" id="sicutXml">.*?</script>\n','',s,flags=re.S)
rep('<script src="https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.9/build/opensheetmusicdisplay.min.js"></script>','<script src="vendor/opensheetmusicdisplay.min.js"></script>')
rep('<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>','<script src="vendor/jszip.min.js"></script>')
cut('/* =========================================================\n   Reading a PDF or photos with Claude','/* =========================================================\n   Library and file opening')

# library kept on this phone
cut('let db=null; const libDocs=new Map();','async function loadLibrary(id){',repl=r'''const libDocs=new Map(), LIBKEY='satb:library', BUNDLED={sicut:'scores/sicut-cervus.xml',hymne:'scores/hymne-a-la-nuit.xml',populus:'scores/populus-sion.gabc',factus:'scores/factus-est.gabc',veni:'scores/veni-sancte-spiritus.gabc'}, bundleCache={};
function libLoad(){ try{ Object.entries(JSON.parse(lsGet(LIBKEY)||'{}')).forEach(([k,v])=>{ if(v&&typeof v.xml==='string') libDocs.set(k,v); }); }catch(e){} }
function libStore(){ try{ localStorage.setItem(LIBKEY,JSON.stringify(Object.fromEntries(libDocs))); return true; }catch(e){ return false; } }
function updateSaveBtn(){ $('saveLib').hidden=!score||currentSource!=='file'; $('delLib').hidden=!currentSource.startsWith('lib:'); $('delLib').textContent='Remove from library'; }
const slug=t=>(String(t).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'')||'score').slice(0,60);
function saveToLibrary(){
  if(!score) return;
  const st=$('status'), id=slug(score.title);
  libDocs.set(id,{title:score.title,composer:score.composer||'',bars:score.measures.length,xml:score.xml.replace(/>\s+</g,'><'),savedAt:Date.now()});
  if(!libStore()){ libDocs.delete(id); st.className='err'; st.textContent='This phone has no room left for the app’s library. Remove a score you no longer need, then try again.'; return; }
  currentSource='lib:'+id; renderLibOptions(); $('lib').value='lib:'+id; updateSaveBtn();
  st.className=''; st.textContent=`Saved “${score.title}” to the library on this phone.`;
}
$('saveLib').addEventListener('click',saveToLibrary);
let delArmed=null;
$('delLib').addEventListener('click',()=>{
  const id=currentSource.slice(4); if(!libDocs.has(id)) return;
  if(!delArmed){ $('delLib').textContent='Tap again to remove'; delArmed=setTimeout(()=>{delArmed=null;updateSaveBtn();},3000); return; }
  clearTimeout(delArmed); delArmed=null;
  const t=libDocs.get(id).title; libDocs.delete(id); libStore(); renderLibOptions();
  $('lib').value='sicut'; loadLibrary('sicut').then(()=>{ $('status').textContent=`Removed “${t}” from the library.`; });
});
function renderLibOptions(){
  $('lib').querySelectorAll('option[value^="lib:"]').forEach(o=>o.remove());
  const keep=$('lib').value;
  [...libDocs].sort((a,b)=>String(a[1].title).localeCompare(String(b[1].title))).forEach(([id,d])=>{
    const o=document.createElement('option'); o.value='lib:'+id; o.textContent=`${d.title}${d.composer?' · '+d.composer:''}`;
    $('lib').insertBefore(o,$('lib').querySelector('option[value="file"]'));
  });
  if(currentSource.startsWith('lib:')&&libDocs.has(currentSource.slice(4))) $('lib').value=currentSource; else if([...$('lib').options].some(o=>o.value===keep)) $('lib').value=keep;
}
function initLibrary(){ libLoad(); renderLibOptions(); updateSaveBtn(); }
''')
rep('''    else if(id==='sicut'){
      if(!sicutCache) sicutCache=document.getElementById('sicutXml').textContent.trim();
      loadScore(parseMusicXML(sicutCache,'Sicut Cervus'));
    } else if(id==='scan'){
      const j=JSON.parse(lsGet('satb:lastScan')||'null'); if(!j) throw new Error();
      loadScore(parseMusicXML(j.xml,j.title));
    } else if(id==='file'&&fileScore) loadScore(fileScore);''','''    else if(BUNDLED[id]){
      if(!bundleCache[id]){ const r=await fetch(BUNDLED[id]); if(!r.ok) throw new Error(); bundleCache[id]=await r.text(); }
      loadScore(parseMusicXML(bundleCache[id],id));
    } else if(id==='file'&&fileScore) loadScore(fileScore);''')
rep('''    } else {
      if(scanning){ st.className='err'; st.textContent='A score is already being read. Stop it first.'; return; }
      await readScoreImages(files);
    }
  }catch(err){ scanning=false; console.error(err); st.className='err'; st.textContent=err.message||'Could not read this file.'; if(!$('scanStop').disabled&&$('scanStop').textContent==='Stop') scanUI(false); }''','''    } else {
      st.className='err'; st.textContent='The app opens MusicXML files only. For a PDF or photos, send them to Claude in your chat and the score will be added to the app.';
    }
  }catch(err){ console.error(err); st.className='err'; st.textContent=err.message||'Could not read this file.'; }''')
rep("let sicutCache=null, fileScore=null, currentSource='sicut';","let fileScore=null, currentSource='sicut';")

rep("  $('coachText').textContent='';\n","")
# coach: no Claude coaching; remember the range start each result was measured from
rep("    getSampler().then(s=>{$('askBox').hidden=!s;});\n","")
cut('let coachCtl=null;',"window.addEventListener('resize',()=>{ clearTimeout(window.__cT)")
rep("coachRes={...r,P,hop,E,dur,voice:v,from:fromBar,to:toBar,bpm,title:score.title,file:f.name};","coachRes={...r,P,hop,E,dur,voice:v,from:fromBar,to:toBar,bpm,rs:rangeStart(),title:score.title,file:f.name};")
rep("const rs=rangeStart(), spb=60/r.bpm;","const rs=r.rs!=null?r.rs:rangeStart(), spb=60/r.bpm;")

# alignment: optional narrow search for live takes (timing already known)
rep('''function alignRec(P,hop,E,dur){''','''function alignRec(P,hop,E,dur,opt){''')
rep('''  let best={sc:-1e18,o:0,k:1}; const oMax=Math.max(0.5,T-dur*0.3);
  for(let k=0.9;k<=1.1001;k+=0.02) for(let o=-1;o<=oMax;o+=0.1){const sc=ev(o,k,10);if(sc>best.sc)best={sc,o,k};}
  const c=best; best={sc:-1e18,o:c.o,k:c.k};
  for(let k=c.k-0.02;k<=c.k+0.0201;k+=0.005) for(let o=c.o-0.15;o<=c.o+0.1501;o+=0.01){const sc=ev(o,k,1);if(sc>best.sc)best={sc,o,k};}''','''  let best={sc:-1e18,o:0,k:1};
  if(opt&&opt.direct){
    for(let o=opt.oMin;o<=opt.oMax+1e-9;o+=0.01){const sc=ev(o,1,1);if(sc>best.sc)best={sc,o,k:1};}
  } else {
    const oMax=Math.max(0.5,T-dur*0.3);
    for(let k=0.9;k<=1.1001;k+=0.02) for(let o=-1;o<=oMax;o+=0.1){const sc=ev(o,k,10);if(sc>best.sc)best={sc,o,k};}
    const c=best; best={sc:-1e18,o:c.o,k:c.k};
    for(let k=c.k-0.02;k<=c.k+0.0201;k+=0.005) for(let o=c.o-0.15;o<=c.o+0.1501;o+=0.01){const sc=ev(o,k,1);if(sc>best.sc)best={sc,o,k};}
  }''')

# playback keeps sounding with the iPhone silent switch on
rep('''function ensureAudio(){
  if(actx) return;''','''function setAudioSession(type){ try{ if(navigator.audioSession) navigator.audioSession.type=type; }catch(e){} }
function ensureAudio(){
  if(actx) return;
  setAudioSession('playback');''')
# ending playback ends a live take
rep('''function halt(){
  clearInterval(timer); timer=null;''','''function halt(){
  if(liveTake&&!liveTake.ending){ liveTake.ending=true; setTimeout(()=>stopLive(true),0); }
  clearInterval(timer); timer=null;''')

# ---------- live singing ----------
LIVE=open('/home/claude/satb-app/tools/chant.js').read()+'\n'+open('/home/claude/satb-app/tools/live.js').read()
rep('''/* ---------- Start ---------- */''',LIVE+'''\n/* ---------- Start ---------- */''')
cut("if(lsGet('satb:lastScan'))","loadLibrary('sicut');")
rep("getSampler().then(s=>{ if(!s) $('hint').textContent='MusicXML (.musicxml, .mxl) opens here. To read a PDF or photos, open this page on claude.ai.'; });\n","")
rep("loadLibrary('sicut');\ninitLibrary();","initLibrary();\nloadLibrary('sicut');\nif('serviceWorker' in navigator) window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));")
rep('</script>\n','</script>\n</body>\n</html>\n') if s.rstrip().endswith('</script>') else None
if not s.rstrip().endswith('</html>'): s=s.rstrip()+'\n</body>\n</html>\n'

exec(open('/home/claude/satb-app/tools/patch_chant.py').read())
for bad in ['getSampler','claude.use','scanUI','readScoreImages','sicutXml','satb:lastScan','askCoach','fonts.googleapis','cdn.jsdelivr','cdnjs']:
    assert bad not in s, 'leftover: '+bad
open('/home/claude/satb-app/index.html','w').write(s)
print('ok', len(s))
