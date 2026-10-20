document.getElementById('year').textContent = new Date().getFullYear();

/* ---------- mobile nav ---------- */
const navToggle = document.getElementById('navToggle');
const navLinks = document.querySelector('.nav-links');
navToggle?.addEventListener('click', () => {
  navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
  navLinks.style.flexDirection = 'column';
  navLinks.style.position = 'fixed';
  navLinks.style.top = '64px';
  navLinks.style.right = '5vw';
  navLinks.style.background = '#FCFDFE';
  navLinks.style.border = '1px solid #C3CFDD';
  navLinks.style.borderRadius = '10px';
  navLinks.style.padding = '16px 22px';
  navLinks.style.gap = '16px';
});
navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  if (window.innerWidth <= 900) navLinks.style.display = 'none';
}));

/* ---------- scroll reveal ---------- */
const revealEls = document.querySelectorAll('.card, .paper-card, .t-item, .edu-item, .contact-card');
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.15 });
revealEls.forEach((el, i) => {
  el.style.animationDelay = `${(i % 4) * 0.08}s`;
  io.observe(el);
});

/* ---------- packet animation along topology ---------- */
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const paths = [
  { d: "M120,80 C260,80 260,180 500,180", color: "#C1622B" },   // Sender A -> bottleneck (Cubic)
  { d: "M120,280 C260,280 260,180 500,180", color: "#2F7B6E" }, // Sender B -> bottleneck (Reno)
  { d: "M500,180 C740,180 740,80 880,80", color: "#3E6FB0" },   // bottleneck -> Receiver A (BBR)
  { d: "M500,180 C740,180 740,280 880,280", color: "#C1622B" }, // bottleneck -> Receiver B
];

const packetsGroup = document.getElementById('packets');

function makeHiddenPath(d) {
  const p = document.createElementNS("http://www.w3.org/2000/svg", "path");
  p.setAttribute("d", d);
  p.setAttribute("fill", "none");
  p.setAttribute("stroke", "none");
  packetsGroup.appendChild(p);
  return p;
}

function spawnPacket(pathData) {
  const guide = makeHiddenPath(pathData.d);
  const len = guide.getTotalLength();
  const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  dot.setAttribute("r", 4.5);
  dot.setAttribute("fill", pathData.color);
  dot.setAttribute("opacity", "0.9");
  packetsGroup.appendChild(dot);

  const duration = 2600 + Math.random() * 1400;
  const start = performance.now();

  function tick(now) {
    const t = Math.min(1, (now - start) / duration);
    const point = guide.getPointAtLength(t * len);
    dot.setAttribute("cx", point.x);
    dot.setAttribute("cy", point.y);
    dot.setAttribute("opacity", t > 0.85 ? String(0.9 * (1 - (t - 0.85) / 0.15)) : "0.9");
    if (t < 1) {
      requestAnimationFrame(tick);
    } else {
      dot.remove();
      guide.remove();
    }
  }
  requestAnimationFrame(tick);
}

if (packetsGroup && !prefersReducedMotion) {
  paths.forEach((p, i) => {
    setInterval(() => spawnPacket(p), 3200 + i * 400);
    setTimeout(() => spawnPacket(p), i * 500);
  });
} else if (packetsGroup) {
  // reduced motion: draw static dots partway along each path instead of animating
  paths.forEach((p) => {
    const guide = makeHiddenPath(p.d);
    const len = guide.getTotalLength();
    const point = guide.getPointAtLength(len * 0.5);
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("r", 4.5);
    dot.setAttribute("cx", point.x);
    dot.setAttribute("cy", point.y);
    dot.setAttribute("fill", p.color);
    packetsGroup.appendChild(dot);
  });
}
