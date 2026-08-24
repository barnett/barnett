(() => {
  const progress = document.querySelector("[data-reading-progress]");
  if (!progress) return;

  const bar = progress.querySelector(".reading-progress-bar");
  if (!bar) return;

  let scheduled = false;

  const render = () => {
    const scrollable = document.documentElement.scrollHeight - window.innerHeight;
    const ratio = scrollable > 0
      ? Math.min(1, Math.max(0, window.scrollY / scrollable))
      : 1;
    const percent = Math.round(ratio * 100);

    bar.style.transform = `scaleX(${ratio})`;
    progress.setAttribute("aria-valuenow", String(percent));
    scheduled = false;
  };

  const schedule = () => {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(render);
  };

  window.addEventListener("scroll", schedule, { passive: true });
  window.addEventListener("resize", schedule);
  window.addEventListener("pageshow", schedule);
  schedule();
})();
