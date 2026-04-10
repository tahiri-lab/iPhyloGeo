const { spawn } = require("child_process");
const path = require("path");

const PAIRS = [
  ["apps/assets/styles/main.scss", "apps/assets/main.css"],
  ["apps/assets/styles/home_page.scss", "apps/assets/home_page.css"],
  ["apps/assets/styles/nav_bar.scss", "apps/assets/nav_bar.css"],
  ["apps/assets/styles/results.scss", "apps/assets/results.css"],
  ["apps/assets/styles/result.scss", "apps/assets/result.css"],
  [
    "apps/assets/styles/params_climatic.scss",
    "apps/assets/params_climatic.css",
  ],
  ["apps/assets/styles/params_genetic.scss", "apps/assets/params_genetic.css"],
  ["apps/assets/styles/upload_page.scss", "apps/assets/upload_page.css"],
  ["apps/assets/styles/utils/button.scss", "apps/assets/button.css"],
  ["apps/assets/styles/utils/popup.scss", "apps/assets/popup.css"],
  ["apps/assets/styles/utils/tooltip.scss", "apps/assets/tooltip.css"],
  ["apps/assets/styles/help.scss", "apps/assets/help.css"],
  ["apps/assets/styles/utils/toast.scss", "apps/assets/toast.css"],
  ["apps/assets/styles/utils/email_input.scss", "apps/assets/email_input.css"],
  ["apps/assets/styles/utils/badge.scss", "apps/assets/badge.css"],
  ["apps/assets/styles/utils/result_card.scss", "apps/assets/result_card.css"],
  ["apps/assets/styles/utils/page_layout.scss", "apps/assets/page_layout.css"],
];

const watchMode = process.argv.includes("--watch");
const args = [];

if (watchMode) {
  args.push("--watch");
}

for (const [src, dest] of PAIRS) {
  args.push(`${src}:${dest}`);
}

const sassBin = path.join(__dirname, "..", "node_modules", ".bin", process.platform === "win32" ? "sass.cmd" : "sass");
const child = spawn(sassBin, args, { stdio: "inherit" });

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 1);
});
