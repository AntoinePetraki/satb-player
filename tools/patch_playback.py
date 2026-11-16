# Lock-screen-proof playback, run by build.py (uses its cut() and rep()).
# Before: a 25 ms timer queued each note 0.25 s ahead. iOS throttles timers when the
# screen locks, so notes were queued too late and dropped. Now the whole passage is
# rendered to one audio buffer per voice and played as a single looping track.
NEW = r'''function synthNote(ctx,dest,m,t,dur){
  const f=440*Math.pow(2,(m+transpose-69)/12);
  const o=ctx.createOscillator(); o.type=isChant()?'triangle':'sawtooth'; o.frequency.value=f;
  const o2=ctx.createOscillator(); o2.type='sine'; o2.frequency.value=f;
  const lp=ctx.createBiquadFilter(); lp.type='lowpass'; lp.frequency.value=Math.min(4200,f*5); lp.Q.value=0.5;
  const g2=ctx.createGain(); g2.gain.value=0.7;
  const env=ctx.createGain();
  env.gain.setValueAtTime(0,t);
  env.gain.linearRampToValueAtTime(0.15,t+0.02);
  env.gain.setTargetAtTime(0.1,t+0.02,0.2);
  const off=t+Math.max(0.06,dur-0.04);
  env.gain.setTargetAtTime(0,off,0.03);
  o.connect(lp); lp.connect(env); o2.connect(g2); g2.connect(env); env.connect(dest);
  o.start(t); o2.start(t); o.stop(off+0.3); o2.stop(off+0.3);
  return {o,o2,env};
}
function playNote(m,t,dur,v){
  const rec=synthNote(actx,vGain[v],m,t,dur); live.add(rec); rec.o.onended=()=>live.delete(rec);
}
function click(t,accent){
  const o=actx.createOscillator(), g=actx.createGain();
  o.frequency.value=accent?1600:1100;
  g.gain.setValueAtTime(0.0001,t); g.gain.exponentialRampToValueAtTime(0.35,t+0.002); g.gain.exponentialRampToValueAtTime(0.0001,t+0.06);
  o.connect(g); g.connect(master); o.start(t); o.stop(t+0.08);
  const rec={o,env:g}; live.add(rec); o.onended=()=>live.delete(rec);
}
/* Render the chosen passage once per voice; replays reuse it until something changes. */
let renderCache=null, startSeq=0;
async function renderVoices(rs,re,spb){
  const key=[score.title,score.end,score.lines.map(l=>l.voice).join(''),rs,re,spb,transpose,isChant()].join('|');
  if(renderCache&&renderCache.key===key) return renderCache;
  renderCache=null;
  const len=(re-rs)*spb, bufs={};
  await Promise.all(VOICES.map(async v=>{
    const ns=voices[v].filter(n=>n.t>=rs-1e-6&&n.t<re-1e-6); if(!ns.length) return;
    let ctx=null;
    for(const sr of [22050,44100]){ try{ ctx=new OfflineAudioContext(1,Math.max(1,Math.ceil((len+0.4)*sr)),sr); break; }catch(e){} }
    if(!ctx) throw new Error('offline');
    ns.forEach(n=>synthNote(ctx,ctx.destination,n.m,(n.t-rs)*spb,Math.min(n.d,re-n.t)*spb));
    bufs[v]=await ctx.startRendering();
  }));
  renderCache={key,bufs,len};
  return renderCache;
}
async function startPlayback(fromBeat,withCount){
  ensureAudio(); actx.resume();
  const my=++startSeq, spb=60/bpm, rs=rangeStart(), re=rangeEnd();
  if(!(fromBeat>=rs && fromBeat<re-1e-6)) fromBeat=rs;
  playing=true; renderPlay();
  const slow=setTimeout(()=>{ if(my===startSeq&&!S0) $('barSub').textContent='Preparing the audio…'; },150);
  let R;
  try{ R=await renderVoices(rs,re,spb); }
  catch(e){ console.error(e); clearTimeout(slow); if(my===startSeq){ playing=false; renderPlay(); $('barSub').textContent='The audio could not be prepared on this device.'; } return; }
  clearTimeout(slow);
  if(my!==startSeq||!playing) return;
  const now=actx.currentTime+0.08; let t0=now;
  if(withCount){ if(isChant()){ const first=voices.S.find(n=>n.t>=fromBeat-1e-6)||voices.S[0]; if(first){ playNote(first.m,now,2*spb,'S'); t0=now+3*spb; } } else {const n=Math.max(1,Math.round(score.beatsPerBar));for(let i=0;i<n;i++) click(now+i*spb,i===0);t0=now+n*spb;} }
  const loop=$('loop').checked, offset=(fromBeat-rs)*spb, srcs=[];
  for(const v of VOICES){
    if(!R.bufs[v]) continue;
    const s=actx.createBufferSource(); s.buffer=R.bufs[v]; s.loop=loop; s.loopStart=0; s.loopEnd=R.len;
    s.connect(vGain[v]); s.start(t0,offset); srcs.push(s);
  }
  const st={spb,rs,re,t0,b0:fromBeat,loop,srcs,passes:[{b0:fromBeat,t0}]};
  S0=st;
  // the end of a passage is signalled by the audio itself, not by a timer
  if(srcs.length) srcs[0].onended=()=>{ if(S0===st&&!st.loop){ halt(); pos=rangeStart(); updateReadout(); refreshView(); } };
  else { halt(); return; }
  lastScrollKey=null;
  try{navigator.wakeLock?.request('screen').then(l=>wl=l).catch(()=>{});}catch(e){}
  renderPlay(); requestAnimationFrame(frame);
}
function currentBeat(){
  if(!S0) return pos;
  const x=(S0.b0-S0.rs)+Math.max(0,actx.currentTime-S0.t0)/S0.spb, len=S0.re-S0.rs;
  return S0.loop?S0.rs+(len>0?x%len:0):Math.min(S0.re,S0.rs+x);
}
/* Turning Loop on or off while playing takes effect at the end of the current pass. */
$('loop').addEventListener('change',()=>{
  if(!S0||!S0.srcs) return;
  const b=currentBeat(); S0.b0=b; S0.t0=Math.max(actx.currentTime,S0.t0); S0.loop=$('loop').checked;
  S0.srcs.forEach(s=>{ s.loop=S0.loop; });
});
function halt(){
  if(liveTake&&!liveTake.ending){ liveTake.ending=true; setTimeout(()=>stopLive(true),0); }
  startSeq++;
  if(S0&&S0.srcs) S0.srcs.forEach(s=>{ try{ s.onended=null; s.stop(); }catch(e){} });
  if(actx){const now=actx.currentTime;live.forEach(r=>{try{r.env.gain.cancelScheduledValues(now);r.env.gain.setTargetAtTime(0,now,0.01);r.o.stop(now+0.06);r.o2&&r.o2.stop(now+0.06);}catch(e){}});}
  live.clear(); S0=null; playing=false;
  try{wl&&wl.release();}catch(e){} wl=null;
  renderPlay();
}
function restartIfPlaying(){ if(playing){const b=currentBeat();halt();startPlayback(b,false);} }
/* Prepare the audio in the background whenever the piece or settings change, so Play starts at once. */
let prepT=null;
function prepareSoon(){
  clearTimeout(prepT);
  prepT=setTimeout(()=>{ if(!score||playing) return; renderVoices(rangeStart(),rangeEnd(),60/bpm).catch(()=>{}); },700);
}
'''
cut("function playNote(m,t,dur,v){", "function togglePlay(){", repl=NEW)

rep("  if(view==='sheet') renderSheet(); else draw();\n}","  if(view==='sheet') renderSheet(); else draw();\n  prepareSoon();\n}")
rep("  if(playing){halt();startPlayback(pos,false);} updateReadout(); refreshView(); refreshCoachSetup();","  if(playing){halt();startPlayback(pos,false);} updateReadout(); refreshView(); refreshCoachSetup(); prepareSoon();")
rep("$('tempo').addEventListener('change',restartIfPlaying);","$('tempo').addEventListener('change',()=>{ restartIfPlaying(); prepareSoon(); });")
rep("restartIfPlaying();refreshCoachSetup();});\n$('tUp')","restartIfPlaying();refreshCoachSetup();prepareSoon();});\n$('tUp')")
rep("$('tUp').addEventListener('click',()=>{transpose=Math.min(12,transpose+1);$('tVal').textContent=(transpose>0?'+':'')+transpose;restartIfPlaying();refreshCoachSetup();});","$('tUp').addEventListener('click',()=>{transpose=Math.min(12,transpose+1);$('tVal').textContent=(transpose>0?'+':'')+transpose;restartIfPlaying();refreshCoachSetup();prepareSoon();});")
