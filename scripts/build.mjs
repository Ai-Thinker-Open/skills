#!/usr/bin/env node

import { readdir, readFile, writeFile, mkdir, stat } from 'fs/promises';
import { join, relative } from 'path';

const SKILLS_DIR = join(process.cwd(), 'skills');
const DIST_DIR = join(process.cwd(), 'dist');

async function ensureDir(dir) {
  try {
    await stat(dir);
  } catch {
    await mkdir(dir, { recursive: true });
  }
}

async function findSkillDirs(dir) {
  const results = [];
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      if (entry.isDirectory()) {
        const skillMd = join(dir, entry.name, 'SKILL.md');
        try {
          await stat(skillMd);
          results.push({ name: entry.name, path: join(dir, entry.name) });
        } catch {
          // Not a skill directory
        }
      }
    }
  } catch (err) {
    // Directory doesn't exist
  }
  return results;
}

async function copyFile(src, dest) {
  const content = await readFile(src);
  await writeFile(dest, content);
}

async function buildSkill(skill) {
  const distSkillDir = join(DIST_DIR, skill.name);
  await ensureDir(distSkillDir);
  
  // Copy SKILL.md
  await copyFile(join(skill.path, 'SKILL.md'), join(distSkillDir, 'SKILL.md'));
  
  // Copy optional directories
  for (const dir of ['scripts', 'references', 'assets', 'agents']) {
    const srcDir = join(skill.path, dir);
    try {
      await stat(srcDir);
      const destDir = join(distSkillDir, dir);
      await ensureDir(destDir);
      
      const files = await readdir(srcDir, { withFileTypes: true });
      for (const file of files) {
        if (file.isFile()) {
          await copyFile(join(srcDir, file.name), join(destDir, file.name));
        }
      }
    } catch {
      // Directory doesn't exist
    }
  }
}

async function generateManifest(skills) {
  const manifest = {
    name: 'seahi-skills',
    version: JSON.parse(await readFile(join(process.cwd(), 'package.json'), 'utf-8')).version,
    description: 'Cross-platform AI Agent Skills collection',
    skills: skills.map(s => ({
      name: s.name,
      path: `./skills/${s.name}`
    }))
  };
  
  await writeFile(
    join(DIST_DIR, 'skills-manifest.json'),
    JSON.stringify(manifest, null, 2)
  );
}

async function main() {
  console.log('🔨 Building skills...\n');
  
  // Clean dist directory
  try {
    const { rm } = await import('fs/promises');
    await rm(DIST_DIR, { recursive: true, force: true });
  } catch {}
  
  await ensureDir(DIST_DIR);
  
  // Find all skills
  const skills = await findSkillDirs(SKILLS_DIR);
  
  if (skills.length === 0) {
    console.log('⚠️  No skills found to build');
    return;
  }
  
  // Build each skill
  for (const skill of skills) {
    console.log(`📦 Building: ${skill.name}`);
    await buildSkill(skill);
  }
  
  // Generate manifest
  await generateManifest(skills);
  
  console.log(`\n✅ Built ${skills.length} skill(s) to dist/`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
