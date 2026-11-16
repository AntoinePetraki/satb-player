/* =========================================================
   Live singing: microphone pitch while the player plays
   ========================================================= */
let liveTake=null, liveLoopPrev=false;
function yinFrame(L){
  const x=L.x, SR=L.sr; let s=0; for(let i=0;i<x.length;i++) s+=x[i]*x[i];
  const rms=Math.sqrt(s/x.length);
  if(rms<L.gate) return {rms,m:NaN};
  const tMin=Math.max(2,Math.floor(SR/L.fmax)), tMax=Math.min(Math.ceil(SR/L.fmin),Math.floor(x.length/2)-2);
  const W=Math.min(x.length-tMax-2,Math.max(256,2*tMax)), d=L.d;
  for(let tau=1;tau<=tMax+1;tau++){let a=0;for(let j=0;j<W;j++){const v=x[j]-x[j+tau];a+=v*v;}d[tau]=a;}
  let run=0; for(let tau=1;tau<=tMax+1;tau++){run+=d[tau];d[tau]=run>0?d[tau]*tau/run:1;}
  let tau=-1;
  for(let t=tMin;t<=tMax;t++){ if(d[t]<0.15){ while(t+1<=tMax&&d[t+1]<d[t]) t++; tau=t; break; } }
  if(tau<0){ let b=tMin; for(let t=tMin;t<=tMax;t++) if(d[t]<d[b]) b=t; if(d[b]<0.3) tau=b; }
  if(tau<1) return {rms,m:NaN};
  const a=d[tau-1],b=d[tau],c=d[tau+1],den=a-2*b+c, sh=den?Math.max(-1,Math.min(1,0.5*(a-c)/den)):0;
  return {rms,m:69+12*Math.log2(SR/(tau+sh)/440)};
}
async function startLive(){
  if(liveTake){ halt(); return; }
  if(!score) return;
  const st=$('coachStatus'); st.className='';
  const v=$('coachVoice').value;
  if(!v){ st.textContent='This score has no part to sing.'; return; }
  const E=expectedNotes(v);
  if(E.length<3){ st.textContent='Choose a few more bars: the coach needs at least three notes of your part.'; return; }
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){ st.className='err'; st.textContent='This browser can’t use the microphone. Open the app from your home screen, or in Safari or Chrome.'; return; }
  halt(); ensureAudio();
  try{ await renderVoices(rangeStart(),rangeEnd(),60/bpm); }catch(e){}
  setAudioSession('play-and-record');
  let stream;
  try{ stream=await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false,noiseSuppression:false,autoGainControl:false}}); }
  catch(e){
    setAudioSession('playback'); st.className='err';
    st.textContent=e&&e.name==='NotAllowedError'?'The microphone isn’t allowed for this app. Allow it in your phone’s settings for the browser you installed the app from, then try again.':'The microphone couldn’t be opened. Close other apps that use it and try again.';
    return;
  }
  await actx.resume();
  const src=actx.createMediaStreamSource(stream), an=actx.createAnalyser();
  an.fftSize=4096; an.smoothingTimeConstant=0; src.connect(an);
  const ds=Math.max(1,Math.round(actx.sampleRate/12000)), sr=actx.sampleRate/ds, [fmin,fmax]=COACH_F[v];
  const cs=getComputedStyle(document.documentElement), col=n=>cs.getPropertyValue(n).trim();
  const ms=E.map(n=>n.m);
  liveTake={stream,src,an,v,E,raw:new Float32Array(an.fftSize),x:new Float32Array(Math.floor(an.fftSize/ds)),d:new Float32Array(Math.floor(an.fftSize/ds)),
    ds,sr,fmin:isChant()?55:fmin/1.6,fmax:isChant()?950:fmax*1.6,pts:[],floor:0.003,gate:0.012,from:fromBar,to:toBar,bpm,rs:rangeStart(),
    lo:Math.min(...ms)-3,hi:Math.max(...ms)+3,frame:0,
    C:{bg:col('--surface'),line:col('--line'),muted:col('--muted'),note:col('--'+v.toLowerCase()),t:col('--t'),a:col('--a'),s:col('--s'),hot:col('--hot')}};
  liveLoopPrev=$('loop').checked; $('loop').checked=false;
  $('liveLabel').textContent='Stop and score'; $('liveStrip').hidden=false; $('liveGot').textContent='Listening…'; $('liveWant').textContent='';
  st.textContent=`Singing ${isChant()?'the chant':VNAME[v]}, ${rangeWord()} ${fromBar}–${toBar}. Your results appear when the passage ends or you tap pause.`;
  pos=rangeStart(); await startPlayback(pos,$('count').checked);
  if(!liveTake) return;
  if(!S0){ stopLive(false); return; }
  liveTake.t0=S0.t0;
  requestAnimationFrame(liveFrame);
}
function liveExpected(L,t){ for(const n of L.E) if(t>=n.s&&t<n.e) return n.m; return null; }
function liveFrame(){
  const L=liveTake; if(!L||L.ending) return;
  L.an.getFloatTimeDomainData(L.raw);
  const x=L.x, ds=L.ds; for(let i=0;i<x.length;i++){let a=0;for(let j=0;j<ds;j++)a+=L.raw[i*ds+j];x[i]=a/ds;}
  const tNow=actx.currentTime-(L.raw.length/actx.sampleRate)/2-L.t0;
  const {rms,m}=yinFrame(L);
  // the silence gate follows the room's noise floor
  L.floor=rms<L.floor?Math.max(0.0005,rms):Math.min(0.02,L.floor*1.0005);
  L.gate=Math.max(0.004,L.floor*4);
  if(tNow>-0.6&&(!L.pts.length||tNow>L.pts[L.pts.length-1][0]+0.004)) L.pts.push([tNow,m]);
  drawLive(L,tNow,m);
  requestAnimationFrame(liveFrame);
}
function drawLive(L,tNow,m){
  const cv=$('liveCv'), dpr=window.devicePixelRatio||1, w=cv.clientWidth, h=cv.clientHeight; if(!w) return;
  if(cv.width!==Math.round(w*dpr)||cv.height!==Math.round(h*dpr)){cv.width=Math.round(w*dpr);cv.height=Math.round(h*dpr);}
  const g=cv.getContext('2d'), C=L.C; g.setTransform(dpr,0,0,dpr,0,0);
  g.fillStyle=C.bg; g.fillRect(0,0,w,h);
  const lo=L.lo, hi=L.hi, rowH=(h-8)/(hi-lo), Y=v=>4+(hi-v)*rowH;
  const nowX=w*0.62, pps=w/5, X=t=>nowX+(t-tNow)*pps;
  g.fillStyle=C.note; g.globalAlpha=0.3;
  L.E.forEach(n=>{ if(n.e<tNow-3.3||n.s>tNow+2) return; g.fillRect(X(n.s),Y(n.m)-rowH/2,Math.max(2,(n.e-n.s)*pps-2),rowH); });
  g.globalAlpha=1;
  g.fillStyle=C.hot; g.fillRect(Math.round(nowX)-1,0,2,h);
  g.lineWidth=2.5; g.lineCap='round';
  let last=null;
  for(let i=L.pts.length-1;i>=0;i--){
    const [t,p]=L.pts[i]; if(t<tNow-3.3) break;
    if(p!==p){last=null;continue;}
    const e=liveExpected(L,t), ref=e!=null?e:(lo+hi)/2, v=ref+wrap12(p-ref), dc=e==null?null:Math.abs(v-e)*100;
    const pt={x:X(t),y:Y(clamp(v,lo,hi)),v};
    if(last&&Math.abs(last.v-v)<1.5){ g.strokeStyle=dc==null?C.muted:dc<25?C.t:dc<50?C.a:C.s; g.beginPath(); g.moveTo(last.x,last.y); g.lineTo(pt.x,pt.y); g.stroke(); }
    last=pt;
  }
  if(++L.frame%6===0){
    const e=liveExpected(L,tNow);
    $('liveWant').innerHTML=e!=null?`Now: <b>${nName(e)}</b>`:(tNow<0?'Get ready…':'Rest');
    if(m!==m) $('liveGot').textContent='Listening…';
    else if(e!=null){ const dv=wrap12(m-e)*100, r=Math.round(dv); $('liveGot').innerHTML=Math.abs(dv)<50?`You: <b>${nName(e)}</b> ${r>0?'+':r<0?'−':'±'}${Math.abs(r)}¢`:`You: <b>${nName(e+dv/100)}</b>`; }
    else $('liveGot').innerHTML=`You: <b>${nName(m)}</b>`;
  }
}
function stopLive(analyse){
  const L=liveTake; if(!L) return; liveTake=null;
  try{L.src.disconnect();}catch(e){} L.stream.getTracks().forEach(t=>t.stop()); setAudioSession('playback');
  $('loop').checked=liveLoopPrev; $('liveLabel').textContent='Sing live'; $('liveStrip').hidden=true;
  if(!analyse) return;
  const st=$('coachStatus'), pts=L.pts, tEnd=pts.length?pts[pts.length-1][0]:0;
  const E=L.E.filter(n=>n.s<tEnd-0.15);
  if(E.length<3){ st.className='err'; st.textContent='That take was too short to score. Sing at least a few notes.'; return; }
  // resample the live readings onto a 10 ms grid starting 0.6 s before the passage
  const hop=0.01, start=-0.6, N=Math.ceil((tEnd-start)/hop)+1, raw=new Float32Array(N).fill(NaN);
  let j=0;
  for(let i=0;i<N;i++){ const t=start+i*hop; while(j<pts.length-1&&Math.abs(pts[j+1][0]-t)<=Math.abs(pts[j][0]-t)) j++; if(Math.abs(pts[j][0]-t)<=0.02) raw[i]=pts[j][1]; }
  const P=new Float32Array(N).fill(NaN);
  for(let i=0;i<N;i++){ if(raw[i]!==raw[i]) continue; const w=[]; for(let k=i-2;k<=i+2;k++) if(k>=0&&k<N&&raw[k]===raw[k]) w.push(raw[k]); w.sort((a,b)=>a-b); P[i]=w[w.length>>1]; }
  const dur=E[E.length-1].e;
  // timing is known from the player; only allow for microphone delay
  const al=alignRec(P,hop,E,dur,{direct:true,oMin:-start-0.1,oMax:-start+0.45});
  if(al.voiced<20||al.match<0.25){ st.className='err'; st.textContent=`Not enough of your singing matched ${isChant()?'the chant':'the '+VNAME[L.v]+' part'}. Check the microphone can hear you clearly and that you sang the ${rangeWord()} shown.`; return; }
  const r=analyseRec(P,hop,E,al);
  const lastBar=Math.max(...E.map(n=>n.bar));
  coachRes={...r,P,hop,E,dur,voice:L.v,from:L.from,to:lastBar,bpm:L.bpm,rs:L.rs,title:score.title,file:'live take'};
  st.className=''; st.textContent=E.length<L.E.length?`Live take scored up to ${unitWord().toLowerCase()} ${lastBar} (you stopped before the end).`:'Live take scored.';
  renderCoach(coachRes);
  $('coach').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
}
$('liveBtn').addEventListener('click',startLive);
