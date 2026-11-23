import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { setTimeout } from "node:timers/promises";

const scratch = process.argv[2];
assert(scratch, "Pass an existing task scratch directory outside cloud sync.");
const capture = process.argv.includes("--capture");
const profile = await mkdtemp(join(resolve(scratch), "kozu-chrome-"));
const chrome = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const browser = spawn(chrome, [
  "--headless", "--disable-background-networking", "--disable-component-update", "--disable-sync",
  "--no-default-browser-check", "--no-first-run", "--remote-debugging-port=0",
  "--user-data-dir=" + profile, "about:blank",
], { stdio: "ignore" });
let socket;
const stopped = new Promise((done) => {
  browser.once("close", done);
  browser.once("error", done);
});

try {
  let port;
  for (let attempt = 0; !port && attempt < 80; attempt += 1) {
    try {
      [port] = (await readFile(join(profile, "DevToolsActivePort"), "utf8")).split("\n");
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      await setTimeout(125);
    }
  }
  assert(port, "Chrome did not expose a local debugger port. Check CHROME and the browser profile path.");
  const targets = await fetch("http://127.0.0.1:" + port + "/json/list").then((response) => response.json());
  socket = new WebSocket(targets.find((target) => target.type === "page").webSocketDebuggerUrl);
  await new Promise((done, fail) => {
    socket.addEventListener("open", done, { once: true });
    socket.addEventListener("error", fail, { once: true });
  });

  let commandId = 0;
  const pending = new Map();
  const requests = [];
  socket.addEventListener("message", ({ data }) => {
    const message = JSON.parse(data);
    if (message.method === "Network.requestWillBeSent") requests.push(message.params.request.url);
    const callback = pending.get(message.id);
    if (!callback) return;
    pending.delete(message.id);
    callback(message);
  });

  const send = (method, params = {}) => new Promise((done, fail) => {
    const id = ++commandId;
    pending.set(id, (message) => {
      if (message.error) fail(new Error(JSON.stringify(message.error)));
      else done(message.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const read = async (expression) => {
    const result = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception.description);
    return result.result.value;
  };
  const press = async (key, virtualKey) => {
    const fields = { key, code: key, windowsVirtualKeyCode: virtualKey };
    await send("Input.dispatchKeyEvent", { ...fields, type: "rawKeyDown" });
    await send("Input.dispatchKeyEvent", { ...fields, type: "keyUp" });
  };
  const clickAt = async (selector) => {
    const [x, y] = await read(`(() => {
      const rect = $(${JSON.stringify(selector)}).getBoundingClientRect();
      return [rect.x + rect.width / 2, rect.y + rect.height / 2];
    })()`);
    await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
    await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
  };
  const viewport = (width, height, mobile = false) =>
    send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
  const shot = async (name) => {
    if (!capture) return;
    const { data } = await send("Page.captureScreenshot", { format: "png" });
    await writeFile(join(scratch, name + ".png"), Buffer.from(data, "base64"));
  };

  await send("Network.enable");
  await send("Page.enable");
  await viewport(1440, 960);
  await send("Page.navigate", { url: new URL("./index.html", import.meta.url).href });
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (await read("document.readyState === 'complete' && document.querySelector('#run-log li') !== null")) break;
    await setTimeout(100);
  }
  assert(await read("document.readyState === 'complete'"));
  await read("Promise.all([...document.images].map((photo) => photo.decode())).then(() => true)");
  await read("document.fonts.ready.then(() => true)");
  assert(await read("[...document.fonts].some(face => face.family === 'Inter' && face.status === 'loaded' && face.weight === '100 900')"), "The bundled Inter face did not load");

  await read(`window.$ = (selector) => document.querySelector(selector);
    window.click = (selector) => $(selector).click();
    window.text = (selector) => $(selector).textContent;
    window.surface = () => document.documentElement.dataset.surface;`);

  assert.equal(await read("surface()"), "paylane");
  assert.equal(await read("text('.balance-value')"), "$117,450.17");
  assert.equal(await read("getComputedStyle($('.balance-cents')).color"), "rgb(100, 107, 112)");
  assert.equal(await read("getComputedStyle($('.kozu-skip')).clipPath"), "inset(50%)");
  assert.equal(await read("$('.kozu-symbols').getBoundingClientRect().height"), 0);
  assert.equal(await read("getComputedStyle($('#listen-status')).clipPath"), "inset(50%)");
  assert.equal(await read("[...document.images].filter(photo => photo.naturalWidth > 0).length"), 3);
  assert.equal(await read("getComputedStyle(document.body).fontFamily.split(',')[0]"), "Inter");
  await shot("paylane-desktop");
  await clickAt("#ledger-toggle");
  assert.equal(await read("$('#older-transactions').hidden"), false);
  await read("click('#ledger-toggle'); $('#dock-home').focus()");
  await press("ArrowRight", 39);
  assert.equal(await read("document.activeElement.id"), "dock-analytics");
  assert.equal(await read("$('#paylane-home').hidden"), true);
  assert.equal(await read("text('#spending-total')"), "$2,174.80");
  assert.equal(await read("getComputedStyle(document.activeElement).outlineStyle"), "none");
  assert.equal(await read("getComputedStyle(document.activeElement).backgroundColor"), "rgb(23, 47, 88)");
  assert(await read("[...document.querySelectorAll('.chart-bar')].some(bar => bar.clientHeight > 20)"));
  assert.equal(await read("getComputedStyle($('.chart-bar')).backgroundColor"), "rgb(119, 141, 172)");
  await read('click(\'[data-period="month"]\')');
  assert.equal(await read("text('#spending-total')"), "$4,535.80");
  await press("End", 35);
  assert.equal(await read("$('#paylane-update').hidden"), false);
  await shot("paylane-update-desktop");
  await read("click('#dock-home'); $('.pay-button').focus(); click('.pay-button')");
  assert.equal(await read("$('#transfer-dialog').open"), true);
  assert.equal(await read("getComputedStyle($('#transfer-dialog'), '::backdrop').backdropFilter"), "blur(40px)");
  await press("Escape", 27);
  assert.equal(await read("$('#transfer-dialog').open"), false);
  assert.equal(await read("document.activeElement.classList.contains('pay-button')"), true);
  await read(`click('.pay-button');
    $('[name=recipient]').value = 'Sample business';
    $('[name=amount]').value = '24.50';
    $('#transfer-form').requestSubmit();`);
  assert.match(await read("text('#transfer-result')"), /24\.50 payment to Sample business/);

  await read("$('#tab-paylane').focus()");
  await press("ArrowRight", 39);
  assert.equal(await read("surface()"), "synq");
  assert.match(await read("getComputedStyle(document.body).fontFamily"), /Helvetica Neue/);
  assert.equal(await read("getComputedStyle($('#new-task')).backdropFilter"), "blur(28px)");
  await read(`click('details[open] [data-agent-action=pause]')`);
  assert.equal(await read("text('details[open] .agent-state')"), "Paused");
  assert.equal(await read("$('details[open] [data-agent-action=advance]').disabled"), true);
  await read(`click('details[open] [data-agent-action=pause]'); click('details[open] [data-agent-action=advance]')`);
  assert.equal(await read("text('details[open] .agent-percent')"), "51%");
  await read("click('#new-task')");
  assert.equal(await read("document.activeElement.id"), "task-input");
  await read("click('#listen')");
  assert.deepEqual(await read("[...$('.waveform').children].map(row => row.children.length)"), [9, 9, 9]);
  assert.equal(await read("getComputedStyle($('.waveform i')).animationName"), "listen-brightness");
  await shot("synq-desktop");
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  assert.equal(await read("$('.waveform').getAnimations({ subtree: true }).length"), 0);
  assert.equal(await read("getComputedStyle($('.waveform i')).opacity"), "0.37");
  await read("click('#listen'); $('#task-form').requestSubmit()");
  assert.match(await read("text('#queued-tasks')"), /prepare a briefing/);

  await read("$('#tab-synq').focus()");
  await press("ArrowRight", 39);
  assert.equal(await read("surface()"), "nightshift");
  assert.equal(await read("getComputedStyle(document.body).fontFamily.split(',')[0]"), "Inter");
  assert.equal(await read("text('#incident-id')"), "INC-3318");
  assert.equal(await read("$('#run-log').children.length"), 5);
  await shot("nightshift-desktop");
  await read("$('#replay-step').focus()");
  await press("ArrowLeft", 37);
  assert.equal(await read("$('#run-log').children.length"), 4);
  assert.equal(await read("$('#replay-step').getAttribute('aria-valuetext')"), "Event 4 of 5");
  assert(await read("$('.terminal-bars .is-future') !== null"));
  await read("$('#tab-eu').focus()");
  await press("End", 35);
  assert.equal(await read("text('#incident-id')"), "INC-3324");
  assert.equal(await read("$('#incident-view').getAttribute('aria-labelledby')"), "tab-stage");
  await read("click('#report-toggle')");
  assert.equal(await read("$('#incident-report').hidden"), false);
  assert.match(await read("text('#report-copy')"), /staging configuration/);
  await read("click('#report-toggle'); click('#tab-eu'); click('#tab-synq')");
  assert.equal(await read("text('details[open] .agent-percent')"), "51%");

  await read("$('#transfer-result').textContent = ''; $('#task-input').value = ''; document.activeElement.blur()");
  for (const width of [390, 320, 768]) {
    await viewport(width, 844, width < 768);
    for (const id of ["paylane", "synq", "nightshift"]) {
      await read("click('#tab-" + id + "'); window.scrollTo(0, 0);");
      assert(await read("document.documentElement.scrollWidth === window.innerWidth"), id + " overflow at " + width);
      const edges = await read(`[...document.querySelectorAll('button, input, textarea, summary, dialog, .kozu-card, .kozu-frost')].filter(el => el.getClientRects().length).some(el => ['Top','Right','Bottom','Left'].some(side => parseFloat(getComputedStyle(el)['border' + side + 'Width']) > 0))`);
      assert(!edges, id + " rendered an element border");
      if (id === "synq") await read("click('#listen')");
      if (width === 390) await shot(id + "-mobile");
      if (id === "synq") await read("click('#listen')");
    }
  }

  await viewport(390, 844, true);
  await read("document.documentElement.style.fontSize = '200%'");
  for (const id of ["paylane", "synq", "nightshift"]) {
    await read("click('#tab-" + id + "')");
    assert(await read("document.documentElement.scrollWidth === window.innerWidth"), id + " overflow at 200% text");
  }
  await read("document.documentElement.style.fontSize = ''");

  const materials = ["blue", "story", "smoke", "agents", "acid", "night"];
  assert(requests.some((url) => url.endsWith("/Fonts/InterVariable.woff2")));
  for (const image of materials) {
    assert(requests.some((url) => url.endsWith("/Assets/Materials/" + image + ".jpg")), image + " was not requested");
  }
  assert(await read(`Promise.all(${JSON.stringify(materials)}.map(name => {
    const image = new Image();
    image.src = '../Assets/Materials/' + name + '.jpg';
    return image.decode();
  })).then(() => true)`));
  assert(!requests.some((url) => /^https?:/.test(url)), "The local reference made a remote request");
  console.log("Chrome passed local assets, keyboard, Paylane, Synq, Nightshift, reduced motion, exact blur and border-free responsive checks.");
} finally {
  socket?.close();
  browser.kill();
  await stopped;
  await rm(profile, { recursive: true, force: true });
}
