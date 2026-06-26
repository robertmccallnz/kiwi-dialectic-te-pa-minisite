/* ── RHIZOME D3.js FORCE-DIRECTED GRAPH ────────────────────────────────
   Replaces the static <canvas> drawRhizome() with an interactive
   force-directed SVG graph powered by D3 v7.
────────────────────────────────────────────────────────────────────── */

let rhizomeSim = null;

function drawRhizomeD3(ranked, eventText) {
  const viz = document.getElementById('rhizomeViz');
  const svgEl = document.getElementById('rhizomeSVG');
  if (!viz || !svgEl) return;

  viz.style.display = 'block';

  const W = 720, H = 400;
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';

  // Stop any previous simulation
  if (rhizomeSim) rhizomeSim.stop();

  // Clear SVG
  const svg = d3.select('#rhizomeSVG');
  svg.selectAll('*').remove();

  // Normalise scores 0–100
  const maxScore = ranked[0][1] || 1;
  const normed = ranked.map(([k, s]) => [k, Math.min(100, Math.round(s / maxScore * 100))]);

  // Build graph data
  const centerNode = { id: '__event__', label: eventText.slice(0, 24) + (eventText.length > 24 ? '…' : ''), isCenter: true, x: W/2, y: H/2, fx: W/2, fy: H/2 };

  const motifNodes = normed.map(([key, score]) => {
    const m = window.MOTIFS[key];
    return { id: key, label: m.name, score, colour: m.colour, realm: m.realm.split('·')[0].trim(), isCenter: false };
  });

  const nodes = [centerNode, ...motifNodes];
  const links = motifNodes.map(n => ({ source: '__event__', target: n.id, score: n.score }));

  // Zoom/pan
  const g = svg.append('g');
  const zoom = d3.zoom().scaleExtent([0.4, 2.5]).on('zoom', (e) => g.attr('transform', e.transform));
  svg.call(zoom);

  // Zoom buttons
  const btnDiv = document.createElement('div');
  btnDiv.className = 'zoom-btn';
  btnDiv.innerHTML = '<button onclick="document.getElementById(\'rhizomeSVG\').dispatchEvent(new CustomEvent(\'zoom-in\'))">+</button><button onclick="document.getElementById(\'rhizomeSVG\').dispatchEvent(new CustomEvent(\'zoom-out\'))">−</button><button onclick="document.getElementById(\'rhizomeSVG\').dispatchEvent(new CustomEvent(\'zoom-reset\'))">⊡</button>';
  // Remove old buttons if present
  viz.querySelectorAll('.zoom-btn').forEach(el => el.remove());
  viz.insertBefore(btnDiv, viz.firstChild);

  svgEl.addEventListener('zoom-in', () => svg.transition().call(zoom.scaleBy, 1.3));
  svgEl.addEventListener('zoom-out', () => svg.transition().call(zoom.scaleBy, 0.75));
  svgEl.addEventListener('zoom-reset', () => svg.transition().call(zoom.transform, d3.zoomIdentity));

  // Background
  g.append('rect').attr('width', W).attr('height', H)
    .attr('fill', isDark ? '#111' : '#f4f0e8').attr('rx', 16);

  // Legend
  g.append('text').attr('class', 'rh-legend')
    .attr('x', 12).attr('y', H - 10)
    .text('Line weight = match strength · Node size = relevance · Drag to explore');

  // Draw links
  const linkSel = g.append('g').selectAll('line').data(links).enter().append('line')
    .attr('class', 'rh-link')
    .attr('stroke', d => {
      const m = window.MOTIFS[d.target.id || d.target];
      return m ? m.colour : '#888';
    })
    .attr('stroke-width', d => 1 + (d.score / 100) * 6)
    .attr('stroke-dasharray', d => d.score < 40 ? '6 5' : 'none');

  // Motif node groups
  const motifSel = g.append('g').selectAll('g.motif-node')
    .data(motifNodes).enter().append('g').attr('class', 'motif-node')
    .call(d3.drag()
      .on('start', function(event, d) {
        if (!event.active) rhizomeSim.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on('drag', function(event, d) { d.fx = event.x; d.fy = event.y; })
      .on('end', function(event, d) {
        if (!event.active) rhizomeSim.alphaTarget(0);
        d.fx = null; d.fy = null;
      })
    );

  const nodeR = d => 18 + (d.score / 100) * 24;

  motifSel.append('circle').attr('class', 'rh-node-circle')
    .attr('r', nodeR)
    .attr('fill', d => d.colour + (d.score > 50 ? 'cc' : '55'))
    .attr('stroke', d => d.colour);

  motifSel.append('text').attr('class', 'rh-node-label')
    .attr('text-anchor', 'middle').attr('dy', d => -(nodeR(d) + 8))
    .attr('font-size', d => 8 + (d.score / 100) * 4)
    .attr('fill', isDark ? '#f0efe9' : '#111')
    .text(d => d.label);

  motifSel.append('text').attr('class', 'rh-node-score')
    .attr('text-anchor', 'middle').attr('dy', '0.35em')
    .attr('font-size', 10)
    .attr('fill', isDark ? '#fff' : '#111')
    .text(d => d.score + '%');

  // Tooltips via title
  motifSel.append('title').text(d => `${d.label}\n${d.realm}\nMatch: ${d.score}%`);

  // Center node
  const cxG = g.append('g').attr('class', 'rh-center');
  const grad = svg.append('defs').append('radialGradient').attr('id', 'cg');
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#c0392b');
  grad.append('stop').attr('offset', '100%').attr('stop-color', '#7b1010');

  cxG.append('circle').attr('class', 'rh-center-circle')
    .attr('cx', W/2).attr('cy', H/2).attr('r', 46)
    .attr('fill', 'url(#cg)').attr('stroke', '#fff').attr('stroke-width', 2);

  const snippet = eventText.slice(0, 32).split(' ');
  const l1 = snippet.slice(0, 3).join(' ');
  const l2 = snippet.slice(3, 6).join(' ') + (eventText.length > 18 ? '…' : '');
  cxG.append('text').attr('class', 'rh-center-label')
    .attr('x', W/2).attr('y', H/2 - 7).attr('text-anchor', 'middle')
    .attr('font-size', 11).text(l1);
  cxG.append('text').attr('class', 'rh-center-label')
    .attr('x', W/2).attr('y', H/2 + 9).attr('text-anchor', 'middle')
    .attr('font-size', 11).text(l2);

  // Force simulation
  rhizomeSim = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(d => 80 + (1 - d.score / 100) * 120).strength(0.6))
    .force('charge', d3.forceManyBody().strength(-180))
    .force('center', d3.forceCenter(W/2, H/2))
    .force('collision', d3.forceCollide().radius(d => d.isCenter ? 52 : nodeR(d) + 12))
    .on('tick', () => {
      linkSel
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      motifSel.attr('transform', d => `translate(${d.x},${d.y})`);
    });
}
