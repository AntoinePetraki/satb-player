# Gregorian chant changes, run by build.py (uses its rep()).
rep("""      <option value="sicut">Sicut Cervus · Palestrina</option>
      <option value="hymne">Hymne à la nuit · Rameau</option>
      <option value="old100">Old Hundredth · hymn</option>""", """      <optgroup label="Choir (SATB)">
        <option value="sicut">Sicut Cervus · Palestrina</option>
        <option value="hymne">Hymne à la nuit · Rameau</option>
        <option value="old100">Old Hundredth · hymn</option>
      </optgroup>
      <optgroup label="Gregorian chant">
        <option value="populus">Pópulus Sion · Introit, Advent II</option>
        <option value="factus">Factus est · Communion, Pentecost</option>
        <option value="veni">Veni Sancte Spiritus · Alleluia, Pentecost</option>
      </optgroup>""")
rep('Opens MusicXML files (.musicxml, .mxl). For a new piece as a PDF or photos, send it to Claude in your chat and it will be added to the app.',
    'Opens MusicXML (.musicxml, .mxl) and Gregorian chant in gabc (.gabc). For a new piece as a PDF or photos, send it to Claude in your chat and it will be added to the app.')
rep('<input id="file" type="file" accept=".musicxml,.xml,.mxl,', '<input id="file" type="file" accept=".musicxml,.xml,.mxl,.gabc,')
rep('    <div id="osmd"></div>', '    <div id="osmd"></div>\n    <div id="chantSvg" hidden></div>')
rep("""  <section>
    <p class="label">Voices to hear</p>""", """  <section id="voicesSec">
    <p class="label">Voices to hear</p>""")
rep("""    <div class="row">
      <div class="name"><strong>Other voices</strong>""", """    <div class="row" id="chantRow" hidden>
      <div class="name"><strong>Pitch</strong><span>Chant has no fixed pitch: pick a comfortable range, then fine-tune with Transpose</span></div>
      <div class="ctl"><div class="seg" role="group" aria-label="Voice range"><button id="cvLow" aria-pressed="true">Low voice</button><button id="cvHigh" aria-pressed="false">High voice</button></div></div>
    </div>
    <div class="row" id="othersRow">
      <div class="name"><strong>Other voices</strong>""")
rep('<div class="name"><strong>Bars</strong><span>Practise one passage</span></div>',
    '<div class="name"><strong id="rangeName">Bars</strong><span id="rangeHint">Practise one passage</span></div>')
rep('<div class="name"><strong>Count-in</strong><span>One bar of clicks before you start</span></div>',
    '<div class="name"><strong id="countName">Count-in</strong><span id="countHint">One bar of clicks before you start</span></div>')
rep('<script src="vendor/jszip.min.js"></script>', '<script src="vendor/jszip.min.js"></script>\n<script src="vendor/exsurge.min.js"></script>')
rep('.spacer{height:24px}', """.spacer{height:24px}
#chantSvg{padding:14px}
#chantSvg svg{display:block;max-width:none}
#chantSvg use.on{fill:var(--hot)}""")

# loading, and the bars/phrases selectors
rep("  coachRes=null; $('coachOut').hidden=true;", "  applyMode(); coachRes=null; $('coachOut').hidden=true;")
rep("""['from','to'].forEach(id=>{$(id).innerHTML=s.measures.map((_,i)=>`<option value="${i+1}">Bar ${i+1}</option>`).join('');});""",
    """['from','to'].forEach(id=>{$(id).innerHTML=s.measures.map((_,i)=>`<option value="${i+1}">${s.phraseLabels?esc(s.phraseLabels[i]):'Bar '+(i+1)}</option>`).join('');});""")
rep("""async function renderSheet(){
  if(!score) return;""", """async function renderSheet(){
  if(!score) return;
  if(isChant()) return renderChantSheet();
  $('chantSvg').hidden=true; $('osmd').hidden=false;""")
rep("function layoutSheet(){", "function layoutSheet(){\n  if(isChant()){ renderChantSheet(); return; }")
rep("""function updateSheet(beat){
  if(!sheet.ready||!score) return;""", """function updateSheet(beat){
  if(isChant()) return updateChantSheet(beat);
  if(!sheet.ready||!score) return;""")
rep("""$('paper').addEventListener('click',e=>{
  if(!sheet.ready) return;""", """$('paper').addEventListener('click',e=>{
  if(isChant()){ chantClick(e); return; }
  if(!sheet.ready) return;""")
rep("if(view==='sheet'&&osmd&&sheet.ready&&Math.abs($('paper').clientWidth-sheet.width)>8){ try{layoutSheet();}catch(e){} }",
    "if(view==='sheet'&&sheet.ready&&(isChant()?Math.abs($('paper').clientWidth-chantMap.width)>8:(osmd&&Math.abs($('paper').clientWidth-sheet.width)>8))){ try{layoutSheet();}catch(e){} }")
rep("""  $('bar').textContent='Bar '+(i+1);
  $('barSub').textContent=`beat ${beatIn} · of ${score.measures.length} bars`;""", """  $('bar').textContent=unitWord()+' '+(i+1);
  $('barSub').textContent=isChant()?`of ${score.measures.length} phrases`:`beat ${beatIn} · of ${score.measures.length} bars`;""")
rep("$('tempoVal').textContent=bpm+' BPM';", "$('tempoVal').textContent=bpm+(isChant()?' /min':' BPM');")
rep("$('tempoSub').textContent=`Original ${score.tempo} BPM · now ${pct}%`;",
    "$('tempoSub').textContent=isChant()?'Notes per minute; a dotted note lasts two':`Original ${score.tempo} BPM · now ${pct}%`;")
rep("$('coachWhat').textContent=`Bars ${fromBar}–${toBar} at ${bpm} BPM",
    "$('coachWhat').textContent=`${isChant()?'Phrases':'Bars'} ${fromBar}–${toBar} at ${bpm} ${isChant()?'notes per minute':'BPM'}")
rep("o.type='sawtooth';", "o.type=isChant()?'triangle':'sawtooth';")
rep("if(withCount){const n=Math.max(1,Math.round(score.beatsPerBar));for(let i=0;i<n;i++) click(now+i*spb,i===0);t0=now+n*spb;}",
    "if(withCount){ if(isChant()){ const first=voices.S.find(n=>n.t>=fromBeat-1e-6)||voices.S[0]; if(first){ playNote(first.m,now,2*spb,'S'); t0=now+3*spb; } } else {const n=Math.max(1,Math.round(score.beatsPerBar));for(let i=0;i<n;i++) click(now+i*spb,i===0);t0=now+n*spb;} }")

# the coach in chant mode
rep("const {P,hop}=await trackPitch(x,CSR,fmin/1.9,fmax*1.9,", "const {P,hop}=await trackPitch(x,CSR,isChant()?55:fmin/1.9,isChant()?950:fmax*1.9,")
rep("const al=alignRec(P,hop,E,dur);", "const al=alignRec(P,hop,E,dur,isChant()?{kMin:0.75,kMax:1.3}:null);")
rep("for(let k=0.9;k<=1.1001;k+=0.02) for(let o=-1;o<=oMax;o+=0.1)",
    "for(let k=(opt&&opt.kMin)||0.9;k<=((opt&&opt.kMax)||1.1)+1e-4;k+=0.02) for(let o=-1;o<=oMax;o+=0.1)")
rep("couldn’t be matched to the ${VNAME[v]} part in bars ${fromBar}–${toBar}.",
    "couldn’t be matched to ${isChant()?'the chant':'the '+VNAME[v]+' part'} in ${rangeWord()} ${fromBar}–${toBar}.")
rep("tile(true,'Overall',r.overall,`${VNAME[r.voice]} · bars ${r.from}–${r.to}`)",
    "tile(true,'Overall',r.overall,`${VNAME[r.voice]} · ${rangeWord()} ${r.from}–${r.to}`)")
rep("""`<li><span class="w"><b>Bar ${b.bar}</b> · ${esc(describeBar(b))}</span><button class="btn" data-bar="${b.bar}">Loop this bar</button></li>`""",
    """`<li><span class="w"><b>${unitWord()} ${b.bar}</b> · ${esc(describeBar(b))}</span><button class="btn" data-bar="${b.bar}">Loop this ${unitWord().toLowerCase()}</button></li>`""")
rep("$('worstH').hidden=!r.worst.length;", "$('worstH').textContent=isChant()?'Phrases to practise':'Bars to practise'; $('worstH').hidden=!r.worst.length;")
rep("return `beat ${+n.beat.toFixed(2)}: you sang about", "return `${isChant()?'':'beat '+(+n.beat.toFixed(2))+': '}you sang about")
rep("Practise the bars listed below slowly with only your part playing, then add the other voices back.",
    "${isChant()?'Practise the phrases listed below slowly, then build back up to speed.':'Practise the bars listed below slowly with only your part playing, then add the other voices back.'}")
rep("and check you recorded the bars set above.", "and check you recorded the ${rangeWord()} set above.")

# library: chant files
rep("if(v&&typeof v.xml==='string') libDocs.set(k,v);", "if(v&&(typeof v.xml==='string'||typeof v.gabcFile==='string')) libDocs.set(k,v);")
rep("libDocs.set(id,{title:score.title,composer:score.composer||'',bars:score.measures.length,xml:score.xml.replace(/>\\s+</g,'><'),savedAt:Date.now()});",
    "libDocs.set(id,isChant()?{kind:'chant',title:score.title,composer:score.composer||'',bars:score.measures.length,gabcFile:`name: ${score.src.title};\\noffice-part: ${score.src.officePart};\\nmode: ${score.src.mode};\\n%%\\n${score.src.gabc}`,savedAt:Date.now()}:{title:score.title,composer:score.composer||'',bars:score.measures.length,xml:score.xml.replace(/>\\s+</g,'><'),savedAt:Date.now()});")
rep("if(id.startsWith('lib:')){ const d=libDocs.get(id.slice(4)); if(!d) throw new Error(); loadScore(parseMusicXML(d.xml,d.title));",
    "if(id.startsWith('lib:')){ const d=libDocs.get(id.slice(4)); if(!d) throw new Error(); loadScore(d.kind==='chant'?chantFromGabc(parseGabcFile(d.gabcFile,d.title)):parseMusicXML(d.xml,d.title));")
rep("loadScore(parseMusicXML(bundleCache[id],id));",
    "loadScore(/\\.gabc$/.test(BUNDLED[id])?chantFromGabc(parseGabcFile(bundleCache[id],id)):parseMusicXML(bundleCache[id],id));")
rep("""  try{
    if(files.some(isXml)){""", """  try{
    const gf=files.find(f=>/\\.gabc$/i.test(f.name));
    if(gf){
      const s=chantFromGabc(parseGabcFile(await gf.text(),gf.name.replace(/\\.[^.]+$/,'')));
      fileScore=s; currentSource='file'; loadScore(s); setLibOption('file',s.title); updateSaveBtn();
      st.textContent=`Loaded the chant “${s.title}”: ${s.measures.length} phrases.`;
      return;
    }
    if(files.some(isXml)){""")

rep("${s.composer?' · '+esc(s.composer):''} · ${s.measures.length} bars`;","${s.composer?' · '+esc(s.composer):''} · ${s.measures.length} ${s.kind==='chant'?'phrases':'bars'}`;")
rep('<div class="name"><strong>Loop</strong><span>Repeat the chosen bars</span></div>','<div class="name"><strong>Loop</strong><span id="loopHint">Repeat the chosen bars</span></div>')
rep('#chantSvg use.on{fill:var(--hot)}', '#chantSvg use.on{fill:var(--hot)}\n.ctl select{min-width:0;flex:1 1 0;text-overflow:ellipsis}')
