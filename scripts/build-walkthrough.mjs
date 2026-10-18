import { mkdir, copyFile, cp } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';

const root = new URL('../', import.meta.url);
const output = new URL('.vercel-static/', root);
await mkdir(output, { recursive: true });
await copyFile(
  new URL('presentation-assets/company-brain-transit-map/index.html', root),
  new URL('index.html', output),
);
await cp(new URL('presentation-assets/company-brain-transit-map/assets/', root),
  new URL('assets/', output), { recursive: true });
console.log(`Built static walkthrough in ${fileURLToPath(output)}`);
