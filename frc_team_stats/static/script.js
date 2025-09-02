// Fetch TBA events & matches from Flask backend
const eventSelect = document.createElement("select");
eventSelect.id = "event-select";
eventSelect.innerHTML = "<option value=''>Select Event</option>";
document.body.insertBefore(eventSelect, document.querySelector("#matches-container"));

fetch("/api/events")
  .then(res=>res.json())
  .then(events=>{
    events.forEach(e=>{
      const opt=document.createElement("option");
      opt.value=e.key;
      opt.textContent=`${e.name} (${e.start_date} → ${e.end_date})`;
      eventSelect.appendChild(opt);
    });
  }).catch(err=>console.error(err));

eventSelect.addEventListener("change", e=>{
  const key=e.target.value;
  if(!key) return;
  const container=document.getElementById("matches-container");
  container.innerHTML="<p>Loading matches...</p>";

  fetch(`/api/matches/${key}`)
    .then(res=>res.json())
    .then(matches=>{
      container.innerHTML="";
      matches.forEach(m=>{
        const div=document.createElement("div");
        div.className="grid-item match-card";
        div.innerHTML=`
          <div class="match-header">${m.comp_level.toUpperCase()} ${m.match_number}</div>
          <div class="alliance red">
            <div>Red Alliance</div>
            <div class="score">${m.alliances.red.score}</div>
          </div>
          <div class="team-list">Teams: ${m.alliances.red.team_keys.join(", ")}</div>
          <div class="alliance blue">
            <div>Blue Alliance</div>
            <div class="score">${m.alliances.blue.score}</div>
          </div>
          <div class="team-list">Teams: ${m.alliances.blue.team_keys.join(", ")}</div>
        `;
        container.appendChild(div);
      });
    })
    .catch(err=>{
      container.innerHTML="<p>Failed to load matches.</p>";
      console.error(err);
    });
});
