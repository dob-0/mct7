const chars = "BRIDGE_STITCH_GHOST_121228#@%&";
setInterval(() => {
  const line = Array.from({length: process.stdout.columns}, () => 
    chars[Math.floor(Math.random() * chars.length)]
  ).join("");
  process.stdout.write(`\x1b[3${Math.floor(Math.random()*7)}m${line}\x1b[0m\n`);
}, 50);
