import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const root = process.cwd();
const target = path.join(root, "contract_report.json");
const backup = path.join(root, ".contract_report.expected.json");

if (!fs.existsSync(target)) {
  console.error("contract_report.json missing. Run npm run contract:generate first.");
  process.exit(1);
}

fs.copyFileSync(target, backup);
execSync("npm run contract:generate", { stdio: "inherit" });

const expected = fs.readFileSync(backup, "utf-8");
const current = fs.readFileSync(target, "utf-8");
fs.unlinkSync(backup);

if (expected !== current) {
  console.error("contract_report.json drift detected. Regenerate and commit artifact.");
  process.exit(1);
}

console.log("contract_report.json is deterministic and up to date.");
