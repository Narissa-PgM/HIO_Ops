/* HIO country atlas. Expects ATLAS_DATA, GEO_MAP and COUNTRY_COORDS from atlas-data.js. */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const E = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

  const host = $('#geo');
  if (host) {
    const data = ATLAS_DATA;
    const bands = [[1,9,'#e6eef3'],[10,49,'#b9d1de'],[50,149,'#7da8bc'],[150,499,'#426d88'],[500,Infinity,'#243f5c']];
    const tint = n => bands.find(([low,high])=>n>=low&&n<=high)?.[2]||'#fffdf8';
    const number = value => Number(value).toLocaleString('en-US');
    const fold = value => String(value).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z]/g,'');
    const aliases = {'unitedstatesofamerica':'unitedstates','koreasouth':'southkorea','skorea':'southkorea','korearepublicof':'southkorea','czechrepublic':'czechia','czechrep':'czechia','dominicanrep':'dominicanrepublic','demrepcongo':'democraticrepublicofthecongo','congokinshasa':'democraticrepublicofthecongo','drcongo':'democraticrepublicofthecongo','congobrazzaville':'republicofthecongo','congo':'republicofthecongo','centralafricanrep':'centralafricanrepublic','eqguinea':'equatorialguinea','ivorycoast':'cotedivoire','burma':'myanmar','bosniaandherz':'bosniaandherzegovina','macedonia':'northmacedonia','timorleste':'easttimor','eswatini':'swaziland','las':'laos','laopeoplesdemocraticrepublic':'laos','viet nam':'vietnam','unitedrepublicoftanzania':'tanzania','syrianarabrepublic':'syria','iranislamicrepublicof':'iran','westbankandgaza':'palestine','csudan':'southsudan','ssudan':'southsudan','gnbissau':'guineabissau','bahamasthe':'bahamas','gambiathe':'gambia','czechia':'czechia','cotedivoire':'cotedivoire'};
    const key = value => aliases[fold(value)]||fold(value);
    const notable = new Map([...Object.entries(COUNTRY_COORDS),['Hong Kong',[22.3,114.17]],['Macau',[22.2,113.55]],['Singapore',[1.35,103.82]],['Malta',[35.9,14.4]],['Bermuda',[32.3,-64.75]],['Cayman Islands',[19.3,-81.3]],['Puerto Rico',[18.2,-66.5]],['Mauritius',[-20.2,57.5]],['Bahrain',[26,50.55]],['Jersey',[49.2,-2.13]],['Barbados',[13.2,-59.5]]].map(([name,point])=>[key(name),point]));
    host.innerHTML = `<div class="atlas-intro"><p>Explore Harvard enrollment evidence by year, School and primary citizenship. Choose a country on the map or search the list.</p></div>
      <div class="geo-control atlas-filters"><label>Series <select id="geoDataset"><option value="citizenship">OIRA · nonresident students</option><option value="historic">Historical HIO student series</option></select></label><label>Fall year <select id="geoYear"></select></label><label>School <select id="geoSchool"><option value="all">All School columns</option>${data.schoolNames.map((name,index)=>`<option value="${index}">${E(name)}</option>`).join('')}</select></label><label>Country <input type="search" id="geoSearch" placeholder="Search country"></label></div>
      <p class="atlas-source-note" id="atlasSource" aria-live="polite"></p>
      <div class="geo-visual atlas-evidence"><div class="geo-map-wrap">${GEO_MAP}<div id="atlasKey" class="atlas-key"></div></div><div class="geo-side"><div class="atlas-detail" id="atlasDetail" aria-live="polite"></div><h4>Countries in this view</h4><div id="geoRank" class="geo-rank" role="group" aria-label="Countries and counts"></div></div></div>
      <details class="ops-reference"><summary>Year coverage and definitions</summary><table class="atlas-coverage"><thead><tr><th scope="col">Years</th><th scope="col">What was verified</th></tr></thead><tbody><tr><td>2004–2010</td><td>Two historical HIO country rows. Different coverage from the OIRA series.</td></tr><tr><td>2011</td><td>Harvard published regional and selected-country summaries. A comparable country-by-School table was not verified. <a href="https://bpb-us-e1.wpmucdn.com/sites.harvard.edu/dist/6/210/files/2023/02/harvard_fact_book_2011-12_final.pdf" target="_blank" rel="noopener">2011–12 Fact Book ↗</a></td></tr><tr><td>2016–2019, 2023–2024</td><td>Verified excerpts from the published country-by-School tables. Unchecked rows are excluded.</td></tr><tr><td>2020–2022, 2025</td><td>Full country tables. The reconstructed sums were checked against the published School columns.</td></tr><tr><td>2026</td><td>A University-wide OIRA country-by-School table was not verified as of 25 November 2026. <a href="https://registrar.fas.harvard.edu/news/2026/09/fall-2026-enrollment-reports-now-available" target="_blank" rel="noopener">FAS reporting announcement ↗</a></td></tr></tbody></table><p>In the OIRA series the all-Schools view adds the published School columns. A student registered in two Schools can appear in both. Blank or dashed cells within a published row contribute zero to the sum. Gray on the map indicates that no row was verified for that location in the selected view.</p><p>Historical HIO rows use a separate series with no School breakdown. <a href="https://oira.harvard.edu/historical-fact-book-archive/" target="_blank" rel="noopener">OIRA Fact Book archive ↗</a></p></details>`;
    const series=$('#geoDataset'),year=$('#geoYear'),school=$('#geoSchool'),search=$('#geoSearch');
    const mapPaths=$$('.land-country',host);
    const overlay=$('#geo-map-overlay',host);
    let selected='',rows=[],byKey=new Map();

    function updateYears(){
      const years=Object.keys(data[series.value]).sort((a,b)=>Number(b)-Number(a));
      year.innerHTML=years.map(value=>`<option value="${value}">${value}${data[series.value][value].coverage==='partial'?' · partial':''}</option>`).join('');
      school.disabled=series.value==='historic';
    }
    function choose(name){
      selected=name;
      const info=byKey.get(key(name));
      const historical=series.value==='historic';
      const measure=historical?'Historical HIO student count':school.value==='all'?'Sum of School columns':data.schoolNames[Number(school.value)]+' count';
      $('#atlasDetail').innerHTML='<h4>'+E(info?.name||name)+'</h4>'+
        (info?'<p><strong class="atlas-count">'+number(info.count)+'</strong><br>'+E(measure)+'</p>':'<p>No verified observation for this selection.</p>');
      for(const row of $$('#geoRank button'))row.setAttribute('aria-pressed',String(row.dataset.country===info?.name));
      for(const path of mapPaths)path.classList.toggle('atlas-selected',key(path.dataset.land)===key(name));
    }
    function draw(){
      const current=data[series.value][year.value];
      const historical=series.value==='historic';
      const sourceEntries=Object.entries(current.rows);
      const comparable=sourceEntries.filter(([name])=>!/^(?:other\/unknown|unknown|na|total)$/i.test(name));
      const needle=fold(search.value);
      rows=comparable.map(([name,values])=>({name,count:historical?values:school.value==='all'?values.reduce((a,b)=>a+b,0):values[Number(school.value)]}));
      byKey=new Map(rows.map(row=>[key(row.name),row]));
      const visible=rows.filter(row=>!needle||fold(row.name).includes(needle)||key(row.name).includes(needle)).sort((a,b)=>b.count-a.count||a.name.localeCompare(b.name));
      const filteredKeys=new Set(visible.map(row=>key(row.name)));
      const seen=new Set();
      const measure=historical?'HIO historical student counts':'OIRA nonresident counts by primary citizenship';
      const coverage=current.coverage==='full'?'Full source table':'Verified excerpt';
      const unit=historical?'':school.value==='all'?' · School-column sums':' · '+data.schoolNames[Number(school.value)];
      const discrepancy=!historical&&year.value==='2025'&&school.value==='all'?' 6,836 School-column entries across all rows; Harvard reports 6,749 unique nonresident students.':'';
      $('#atlasSource').innerHTML='<strong>'+E(year.value+' · '+coverage)+'</strong><span>'+E(measure+unit+' · '+rows.length+' named rows.'+discrepancy)+'</span><a href="'+current.url+'" target="_blank" rel="noopener">Open source table ↗</a>';
      for(const path of mapPaths){
        const code=key(path.dataset.land);
        const row=byKey.get(code);
        seen.add(code);
        const shown=!!row&&filteredKeys.has(code);
        path.style.fill=shown?tint(row.count):'#e1e7e7';
        path.setAttribute('tabindex',shown?'0':'-1');
        path.setAttribute('role','button');
        const label=shown?row.name+': '+number(row.count):path.dataset.land+': no observation shown';
        path.setAttribute('aria-label',label);
        let title=path.querySelector('title');
        if(!title){title=document.createElementNS('http://www.w3.org/2000/svg','title');path.append(title);}
        title.textContent=label;
      }
      overlay.innerHTML=visible.filter(row=>notable.has(key(row.name))&&(!seen.has(key(row.name))||row.count>=150)).map(row=>{
        const [lat,lon]=notable.get(key(row.name));
        const x=(lon+180)*960/360,y=(90-lat)*505/180;
        return '<circle data-place="'+E(row.name)+'" cx="'+x+'" cy="'+y+'" r="'+(seen.has(key(row.name))?'3.5':'4.5')+'" fill="'+tint(row.count)+'" stroke="#243f5c"><title>'+E(row.name+': '+number(row.count))+'</title></circle>';
      }).join('');
      $('#atlasKey').innerHTML=bands.map(([low,high,color])=>'<span><i style="background:'+color+'"></i>'+low+(Number.isFinite(high)?'–'+high:'+')+'</span>').join('')+'<span><i style="background:#fffdf8"></i>0 in source row</span><span><i style="background:#e1e7e7"></i>Missing or outside search</span>';
      $('#geoRank').innerHTML=visible.length?visible.map(row=>'<button type="button" class="geo-rank-row" data-country="'+E(row.name)+'" aria-pressed="false"><span>'+E(row.name)+'</span><b>'+number(row.count)+'</b></button>').join(''):'<p>No matching verified rows.</p>';
      if(selected&&filteredKeys.has(key(selected)))choose(selected);
      else if(needle&&visible.length===1)choose(visible[0].name);
      else{
        selected='';
        mapPaths.forEach(path=>path.classList.remove('atlas-selected'));
        $('#atlasDetail').innerHTML='<h4>Select a country</h4><p>Read its count and the measure behind it.</p>';
      }
    }
    function selectFromEvent(event){
      const path=event.target.closest('.land-country');
      const button=event.target.closest('[data-country],[data-place]');
      if(path)choose(byKey.get(key(path.dataset.land))?.name||path.dataset.land);
      else if(button)choose(button.getAttribute('data-country')||button.getAttribute('data-place'));
    }
    host.addEventListener('click',selectFromEvent);
    host.addEventListener('keydown',event=>{
      if(event.target.matches('.land-country')&&['Enter',' '].includes(event.key)){event.preventDefault();selectFromEvent(event);}
    });
    series.addEventListener('change',()=>{selected='';updateYears();draw();});
    year.addEventListener('change',draw);
    school.addEventListener('change',draw);
    search.addEventListener('input',draw);
    updateYears();
    draw();
  }
