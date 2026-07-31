#!/usr/bin/env node

import { writeFile } from 'fs/promises';
import { join } from 'path';

import {
  buildManifest,
  computeSkillHashes,
  manifestJson
} from './lib/skill-hash.mjs';

const REPO_ROOT = process.cwd();
const OUT_PATH = join(REPO_ROOT, 'skills-manifest.json');

async function main() {
  console.log('📋 Generating skills manifest...');

  const skills = await computeSkillHashes(REPO_ROOT);
  const names = Object.keys(skills);

  if (names.length === 0) {
    console.warn('⚠️  No tracked skills found under skills/ (did you `git add` new skills?).');
  }

  await writeFile(OUT_PATH, manifestJson(buildManifest(skills)), 'utf8');

  console.log(`✅ Wrote ${OUT_PATH} (${names.length} skill(s))`);
  for (const name of names) {
    const skill = skills[name];
    console.log(`   ${name}: ${skill.hash} (${skill.files} file(s), ${skill.size} bytes)`);
  }
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
