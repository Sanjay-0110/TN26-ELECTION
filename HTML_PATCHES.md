# HTML Patches Required
## How to connect the new JS files to each HTML page

Each HTML file needs:
1. Script tags loading the JS files (in `<head>` or before `</body>`)
2. `id` attributes on the elements the JS targets

---

## Script tags to add to EVERY page (before `</body>`)

```html
<!-- External chart library -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<!-- Dashboard scripts (order matters) -->
<script src="js/data-loader.js"></script>
<script src="js/stats-calculator.js"></script>
<script src="js/chart-builder.js"></script>
<script src="js/table-manager.js"></script>
<script src="js/filter-handler.js"></script>
<script src="js/ui-controller.js"></script>
```

---

## index.html — IDs to add

### Donut ring SVG circles
The two `<circle>` elements inside the `.relative.w-80.h-80` div need IDs:

```html
<!-- NP Segment — add id="ring-np" -->
<circle id="ring-np" cx="50" cy="50" fill="none" r="45"
  stroke="#00daf3" stroke-dasharray="172 282.7"
  stroke-linecap="round" stroke-width="8"></circle>

<!-- DM-X Segment — add id="ring-dmx" -->
<circle id="ring-dmx" cx="50" cy="50" fill="none" r="45"
  stroke="#ffe16d" stroke-dasharray="113 282.7" stroke-dashoffset="-172"
  stroke-linecap="round" stroke-width="8"></circle>
```

### Donut legend numbers (the "128", "84", "22" spans)
```html
<!-- New Party number -->
<p id="ring-label-np" class="font-headline-lg text-headline-lg">128</p>

<!-- DM-X number -->
<p id="ring-label-dmx" class="font-headline-lg text-headline-lg text-on-surface">84</p>

<!-- AD-Y number -->
<p id="ring-label-ady" class="font-headline-lg text-headline-lg text-on-surface-variant">22</p>

<!-- Centre total -->
<h2 id="ring-total" class="font-display-lg text-display-lg text-on-surface">234</h2>
```

### Metric card – aggregate swing value
```html
<!-- Change "+28.4" to: -->
<h3 class="font-display-lg text-display-lg text-primary-fixed-dim">
  <span id="card-aggregate-swing">+28.4</span><span class="text-2xl font-light">%</span>
</h3>
```

### Critical Constituency Shifts table body
```html
<!-- Replace the hardcoded <tbody> rows with an empty tbody: -->
<tbody id="index-shifts-tbody" class="text-body-md text-body-md text-on-surface-variant">
</tbody>
```

---

## swing_analysis.html — IDs to add

### Hero summary card values
```html
<!-- "New Party Gains" card value -->
<h2 id="swing-hero-np-gains" class="font-display-lg text-display-lg text-primary-fixed-dim">+108</h2>

<!-- "Total Seats" card value -->
<h2 id="swing-hero-total" class="font-display-lg text-display-lg text-on-surface">234</h2>

<!-- "Swing Seats" card value -->
<h2 id="swing-hero-swing-seats" class="font-display-lg text-display-lg text-on-surface">112</h2>
```

### Seat Transition Matrix tbody
```html
<tbody id="swing-matrix-tbody" class="divide-y divide-outline-variant/30">
  <!-- JS will populate this -->
</tbody>
```

### Vote Share Churn bars (inside the "Vote Share Churn" card)
Replace the three static bar blocks with:

```html
<!-- NP bar -->
<div>
  <div class="flex justify-between items-end mb-2">
    <span class="font-label-md text-on-surface">New Party (TVK)</span>
    <span id="churn-pct-np" class="font-label-sm text-primary-fixed-dim">28.4%</span>
  </div>
  <div class="w-full bg-surface-container-highest h-2 rounded-full overflow-hidden">
    <div id="churn-bar-np" class="bg-primary-fixed-dim h-full rounded-full shadow-[0_0_10px_rgba(0,218,243,0.5)]" style="width:28.4%"></div>
  </div>
</div>

<!-- DMK+ bar -->
<div>
  <div class="flex justify-between items-end mb-2">
    <span class="font-label-md text-on-surface">DMK+ Alliance</span>
    <span id="churn-pct-dmx" class="font-label-sm text-secondary-fixed-dim">34.2%</span>
  </div>
  <div class="w-full bg-surface-container-highest h-2 rounded-full overflow-hidden">
    <div id="churn-bar-dmx" class="bg-secondary-fixed-dim h-full rounded-full" style="width:34.2%"></div>
  </div>
</div>

<!-- ADMK+ bar -->
<div>
  <div class="flex justify-between items-end mb-2">
    <span class="font-label-md text-on-surface">AIADMK+ Alliance</span>
    <span id="churn-pct-ady" class="font-label-sm text-outline">21.5%</span>
  </div>
  <div class="w-full bg-surface-container-highest h-2 rounded-full overflow-hidden">
    <div id="churn-bar-ady" class="bg-outline h-full rounded-full" style="width:21.5%"></div>
  </div>
</div>
```

### Vote Share Bar Chart canvas (add inside the col-span-8 Seat Transition card, or a new card)
```html
<div class="mt-6" style="height:280px; position:relative;">
  <canvas id="swingVoteShareChart"></canvas>
</div>
```

---

## demographic.html — IDs to add

### Demographic bar elements — add `data-bar-height` attributes
Each `.bg-primary-container` bar div needs a `data-bar-height` attribute matching its current inline height:

```html
<!-- Example for the 18-24 bar: -->
<div class="w-1/2 bg-primary-container h-[72%] rounded-t-sm glow-cyan relative group"
     data-bar-height="72%"></div>

<!-- Repeat for all bars: 25-34 (78%), 35-54 (82%), 55-64 (68%), 65+ (88%) -->
```

### Party vote doughnut chart canvas (add inside or below Age Group section)
```html
<div class="mt-8" style="height:240px; position:relative;">
  <canvas id="demoPartyVoteChart"></canvas>
</div>
```

### Regional Performance Matrix tbody (optional live data)
```html
<tbody id="demo-vote-tbody">
  <!-- populated by JS if present -->
</tbody>
```

---

## regional.html — IDs to add

### Region cards in the right inspector panel

**North TN card:**
```html
<p id="region-north-leading-pct" class="font-body-lg text-body-lg text-primary-fixed-dim">64%</p>
<p id="region-north-margin"      class="font-body-lg text-body-lg text-on-surface">+8.2k</p>
<div id="region-north-np-bar"    class="absolute h-full left-0 bg-primary-fixed-dim" style="width:64%"></div>
<div id="region-north-opp-bar"   class="absolute h-full right-0 bg-secondary-fixed"  style="width:36%"></div>
```

**West TN card:**
```html
<p id="region-west-leading-pct" ...>78%</p>
<p id="region-west-margin"      ...>+22k</p>
<div id="region-west-np-bar"    ...></div>
<div id="region-west-opp-bar"   ...></div>
```

**South TN card:**
```html
<p id="region-south-leading-pct" ...>49%</p>
<p id="region-south-margin"      ...>+1.2k</p>
<div id="region-south-np-bar"    ...></div>
<div id="region-south-opp-bar"   ...></div>
```

### Legend stats (floating bottom-right)
```html
<p id="regional-total-seats"    class="font-headline-md text-headline-md text-on-surface">234</p>
<p id="regional-declared-seats" class="font-headline-md text-headline-md text-secondary-fixed">142</p>
<p id="regional-pending-seats"  class="font-headline-md text-headline-md text-on-surface">92</p>
```

### Optional: constituency list sidebar
```html
<div id="regional-constituency-list" class="mt-4 space-y-1 overflow-y-auto max-h-64">
  <!-- populated by JS -->
</div>
```

---

## coalition.html — IDs to add

### Strike rate bars
```html
<!-- DM-X bar -->
<div id="coalition-bar-dmx" class="h-full bg-primary-fixed-dim w-[84.2%] transition-all duration-1000"></div>
<span id="coalition-rate-dmx"  class="font-label-md text-label-md text-primary-fixed-dim">84.2% Strike Rate</span>
<span id="coalition-seats-dmx" class="font-label-sm">155/184 Seats</span>

<!-- AD-Y bar -->
<div id="coalition-bar-ady" class="h-full bg-secondary-fixed-dim w-[41.8%] transition-all duration-1000"></div>
<span id="coalition-rate-ady"  class="font-label-md text-label-md text-secondary-fixed-dim">41.8% Strike Rate</span>
<span id="coalition-seats-ady" class="font-label-sm">62/148 Seats</span>

<!-- NEW bar -->
<div id="coalition-bar-new" class="h-full bg-tertiary w-[22.5%] transition-all duration-1000"></div>
<span id="coalition-rate-new"  class="font-label-md text-label-md text-tertiary">22.5% Strike Rate</span>
<span id="coalition-seats-new" class="font-label-sm">18/80 Seats</span>
```

### Partner Efficiency Matrix tbody
```html
<tbody id="coalition-partner-tbody" class="font-body-md text-body-md">
  <!-- populated by JS -->
</tbody>
```

### Vote Share Migration chart canvas
Replace the static bar-chart divs in the "Vote Share Migration" section with:
```html
<div style="height:240px; position:relative;">
  <canvas id="coalitionMigrationChart"></canvas>
</div>
```

### Swing stat card
```html
<p id="coalition-swing-incumbency" class="font-display-lg text-[32px] text-primary-fixed-dim">+4.8%</p>
```

---

## Quick summary of new IDs across all pages

| Page           | New ID(s) added                                                                                      |
|----------------|------------------------------------------------------------------------------------------------------|
| index          | `ring-np`, `ring-dmx`, `ring-total`, `ring-label-np/dmx/ady`, `card-aggregate-swing`, `index-shifts-tbody` |
| swing_analysis | `swing-hero-np-gains`, `swing-hero-total`, `swing-hero-swing-seats`, `swing-matrix-tbody`, `churn-bar-np/dmx/ady`, `churn-pct-np/dmx/ady`, `swingVoteShareChart` |
| demographic    | `data-bar-height` attrs on bars, `demoPartyVoteChart`, `demo-vote-tbody`                              |
| regional       | `region-north/west/south-*`, `regional-total/declared/pending-seats`, `regional-constituency-list`   |
| coalition      | `coalition-bar-dmx/ady/new`, `coalition-rate-*`, `coalition-seats-*`, `coalition-partner-tbody`, `coalitionMigrationChart`, `coalition-swing-incumbency` |
