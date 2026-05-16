#!/usr/bin/env node
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = path.resolve(path.dirname(__filename), "..");

function parseArgs(argv) {
  const args = { quiet: false };
  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--quiet") {
      args.quiet = true;
    } else if (arg.startsWith("--")) {
      const key = arg.slice(2).replaceAll("-", "_");
      args[key] = argv[index + 1];
      index += 1;
    }
  }
  return args;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function resolveRun(args) {
  if (args.manifest) {
    const manifestPath = path.resolve(args.manifest);
    const manifest = readJson(manifestPath);
    const outputDir = path.resolve(ROOT, manifest.scope.output_dir);
    const html = args.html ? path.resolve(args.html) : path.join(outputDir, "report.html");
    const out = args.out ? path.resolve(args.out) : path.join(outputDir, "browser_qa_summary.json");
    const screenshots = args.screenshots ? path.resolve(args.screenshots) : outputDir;
    const bundle = args.bundle ? path.resolve(args.bundle) : path.join(outputDir, "report_bundle.json");
    return { manifestPath, manifest, outputDir, html, out, screenshots, bundle };
  }
  if (!args.html) {
    throw new Error("--manifest or --html is required");
  }
  const html = path.resolve(args.html);
  const outputDir = path.dirname(html);
  return {
    manifestPath: null,
    manifest: null,
    outputDir,
    html,
    out: args.out ? path.resolve(args.out) : path.join(outputDir, "browser_qa_summary.json"),
    screenshots: args.screenshots ? path.resolve(args.screenshots) : outputDir,
    bundle: args.bundle ? path.resolve(args.bundle) : path.join(outputDir, "report_bundle.json"),
  };
}

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".html") return "text/html; charset=utf-8";
  if (ext === ".js") return "text/javascript; charset=utf-8";
  if (ext === ".css") return "text/css; charset=utf-8";
  if (ext === ".json") return "application/json; charset=utf-8";
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".svg") return "image/svg+xml";
  return "application/octet-stream";
}

function startServer(rootDir) {
  const server = http.createServer((request, response) => {
    try {
      const rawUrl = new URL(request.url || "/", "http://127.0.0.1");
      let requested = decodeURIComponent(rawUrl.pathname);
      if (requested === "/") requested = "/report.html";
      const filePath = path.resolve(rootDir, `.${requested}`);
      if (!filePath.startsWith(rootDir)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      response.writeHead(200, { "Content-Type": contentType(filePath) });
      fs.createReadStream(filePath).pipe(response);
    } catch (error) {
      response.writeHead(500);
      response.end(String(error?.message || error));
    }
  });
  return new Promise((resolve) => {
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolve({ server, port: address.port });
    });
  });
}

function closeServer(server) {
  return new Promise((resolve) => server.close(resolve));
}

function money(value, digits = 0) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  }).format(Number(value || 0));
}

function pct(value) {
  return `${(Number(value || 0) * 100).toFixed(1)}%`;
}

function expectedChecks(bundle) {
  const scope = bundle.scope || {};
  const currentLabel = scope.current_period_label || `${scope.current_start} to ${scope.current_end}`;
  const affiliate = bundle.metrics?.affiliate_current || {};
  const target = bundle.target_summary?.current || {};
  return {
    h1Includes: ["eufyMake", scope.market, currentLabel].filter(Boolean),
    bodyIncludes: [
      currentLabel,
      money(affiliate.revenue, 2),
      money(affiliate.revenue, 0),
      String(affiliate.orders || 0),
      pct(target.current_period_pacing),
    ],
  };
}

async function launchBrowser(chromium) {
  try {
    return await chromium.launch({ headless: true });
  } catch (firstError) {
    try {
      return await chromium.launch({ channel: "chrome", headless: true });
    } catch {
      throw firstError;
    }
  }
}

async function inspectViewport(browser, url, viewport, screenshotPath, bundle, label) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1, isMobile: label === "mobile" });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });
  page.on("pageerror", (error) => pageErrors.push(error.message));

  const response = await page.goto(url, { waitUntil: "networkidle", timeout: 30_000 });
  await page.screenshot({ path: screenshotPath, fullPage: true });

  const dom = await page.evaluate(() => {
    const h1 = document.querySelector("h1")?.innerText || "";
    const bodyText = document.body?.innerText || "";
    const doc = document.documentElement;
    const horizontalOverflow = doc.scrollWidth > doc.clientWidth + 1;
    const tableChecks = [...document.querySelectorAll("table")].map((table) => {
      let wrapper = table.parentElement;
      let scrollable = false;
      while (wrapper && wrapper !== document.body) {
        const style = getComputedStyle(wrapper);
        if (["auto", "scroll", "overlay"].includes(style.overflowX)) {
          scrollable = wrapper.scrollWidth > wrapper.clientWidth;
          break;
        }
        wrapper = wrapper.parentElement;
      }
      return {
        tableScrollWidth: table.scrollWidth,
        tableClientWidth: table.clientWidth,
        internalScroll: table.scrollWidth <= table.clientWidth || scrollable,
      };
    });
    return { h1, bodyText, horizontalOverflow, tableChecks };
  });

  const expected = expectedChecks(bundle);
  const h1Failures = expected.h1Includes.filter((item) => !dom.h1.includes(item));
  const bodyFailures = expected.bodyIncludes.filter((item) => !dom.bodyText.includes(item));
  const mobileTablesScrollInternally = dom.tableChecks.every((item) => item.internalScroll);

  await context.close();
  return {
    label,
    http_status: response?.status() || 0,
    console_errors: consoleErrors.length + pageErrors.length,
    console_error_samples: [...consoleErrors, ...pageErrors].slice(0, 5),
    horizontal_overflow: dom.horizontalOverflow,
    mobile_tables_scroll_internally: label === "mobile" ? mobileTablesScrollInternally : true,
    h1_bundle_failures: h1Failures,
    body_bundle_failures: bodyFailures,
    screenshot: screenshotPath,
  };
}

function summarize(status, run, extra = {}) {
  return {
    status,
    html: path.relative(run.outputDir, run.html),
    output_dir: run.outputDir,
    desktop_console_errors: extra.desktop?.console_errors ?? 0,
    mobile_console_errors: extra.mobile?.console_errors ?? 0,
    horizontal_overflow: Boolean(extra.desktop?.horizontal_overflow || extra.mobile?.horizontal_overflow),
    desktop: extra.desktop || null,
    mobile: extra.mobile || null,
    failed_checks: extra.failed_checks || [],
    server_closed: Boolean(extra.server_closed),
    error: extra.error,
  };
}

async function main() {
  const args = parseArgs(process.argv);
  const run = resolveRun(args);
  ensureDir(path.dirname(run.out));
  ensureDir(run.screenshots);

  if (!fs.existsSync(run.html)) {
    const summary = summarize("failed", run, { failed_checks: ["html_exists"], error: `Missing HTML file: ${run.html}` });
    fs.writeFileSync(run.out, `${JSON.stringify(summary, null, 2)}\n`);
    console.log(JSON.stringify({ status: "failed", failed_checks: summary.failed_checks, browser_qa_summary: run.out }));
    return 2;
  }
  if (!fs.existsSync(run.bundle)) {
    const summary = summarize("failed", run, { failed_checks: ["bundle_exists"], error: `Missing bundle file: ${run.bundle}` });
    fs.writeFileSync(run.out, `${JSON.stringify(summary, null, 2)}\n`);
    console.log(JSON.stringify({ status: "failed", failed_checks: summary.failed_checks, browser_qa_summary: run.out }));
    return 2;
  }

  let serverRecord = null;
  try {
    const { chromium } = await import("playwright");
    const bundle = readJson(run.bundle);
    serverRecord = await startServer(path.dirname(run.html));
    const url = `http://127.0.0.1:${serverRecord.port}/${path.basename(run.html)}`;
    const browser = await launchBrowser(chromium);
    const desktop = await inspectViewport(
      browser,
      url,
      { width: 1280, height: 720 },
      path.join(run.screenshots, "browser_qa_desktop.png"),
      bundle,
      "desktop",
    );
    const mobile = await inspectViewport(
      browser,
      url,
      { width: 390, height: 844 },
      path.join(run.screenshots, "browser_qa_mobile.png"),
      bundle,
      "mobile",
    );
    await browser.close();

    const failedChecks = [];
    for (const result of [desktop, mobile]) {
      if (result.http_status < 200 || result.http_status >= 400) failedChecks.push(`${result.label}_http_status`);
      if (result.console_errors) failedChecks.push(`${result.label}_console_errors`);
      if (result.horizontal_overflow) failedChecks.push(`${result.label}_horizontal_overflow`);
      if (result.label === "mobile" && !result.mobile_tables_scroll_internally) failedChecks.push("mobile_tables_internal_scroll");
      if (result.h1_bundle_failures.length) failedChecks.push(`${result.label}_h1_bundle_match`);
      if (result.body_bundle_failures.length) failedChecks.push(`${result.label}_kpi_bundle_match`);
    }
    await closeServer(serverRecord.server);
    serverRecord = null;
    const summary = summarize(failedChecks.length ? "failed" : "passed", run, {
      desktop,
      mobile,
      failed_checks: failedChecks,
      server_closed: true,
    });
    fs.writeFileSync(run.out, `${JSON.stringify(summary, null, 2)}\n`);
    console.log(JSON.stringify({
      status: summary.status,
      failed_checks: summary.failed_checks,
      desktop_console_errors: summary.desktop_console_errors,
      mobile_console_errors: summary.mobile_console_errors,
      horizontal_overflow: summary.horizontal_overflow,
      browser_qa_summary: run.out,
    }));
    return failedChecks.length ? 1 : 0;
  } catch (error) {
    if (serverRecord) {
      await closeServer(serverRecord.server);
    }
    const summary = summarize("failed", run, {
      failed_checks: ["browser_qa_runtime"],
      error: String(error?.stack || error?.message || error),
      server_closed: true,
    });
    fs.writeFileSync(run.out, `${JSON.stringify(summary, null, 2)}\n`);
    console.log(JSON.stringify({ status: "failed", failed_checks: summary.failed_checks, browser_qa_summary: run.out }));
    return 2;
  }
}

process.exitCode = await main();
