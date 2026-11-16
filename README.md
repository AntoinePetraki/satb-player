# SATB Part Player

A choir rehearsal app for your phone. Open it at **https://antoinepetraki.github.io/satb-player/**.

- Follow the engraved score: notes turn red as they sound and a line moves with the music.
- Hear any voice (Soprano, Alto, Tenor, Bass) or the full choir, at any tempo, looped, transposed.
- **Voice coach:** sing your part live into the microphone (or upload a recording) and get your pitch drawn over the notes, scores for right notes, intonation and rhythm, and tips.
- **Gregorian chant** in square notation: phrases instead of bars, a low/high voice switch, the starting note before you sing, and the same voice coach.
- Works offline once installed. Opens MusicXML (.musicxml, .mxl) and chant in gabc (.gabc), and keeps them in a library on your phone.

## Install on your phone

**iPhone:** open the link in **Safari**, tap the Share button, then **Add to Home Screen**.
**Android:** open the link in **Chrome**, tap the ⋮ menu, then **Install app** (or **Add to Home screen**).

Included scores: *Sicut Cervus* (Palestrina), *Hymne à la nuit* (Rameau), *Old Hundredth*; chant: *Pópulus Sion*, *Factus est*, *Veni Sancte Spiritus* (gabc transcriptions from the [Gregorio project](https://github.com/gregorio-project/gregorio)).

Chant is drawn with [exsurge](https://github.com/bbloomf/exsurge) (MIT, see `vendor/exsurge-LICENSE.txt`); scores with [OpenSheetMusicDisplay](https://github.com/opensheetmusicdisplay/opensheetmusicdisplay) (BSD-3-Clause).

`tools/` holds the build script used to produce `index.html`; it isn't needed to run the app.
