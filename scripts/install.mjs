#!/usr/bin/env node

import { readdir, stat, mkdir, copyFile, rm } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

const SKILLS_DIR = join(process.cwd(), 'skills');
const TARGET_DIRS = [
  join(process.env.USERPROFILE || '', '.claude', 'skills'),
  join(process.env.USERPROFILE || '', '.codex', 'skills')
];

async function copyDir(src, dest) {
  await mkdir(dest, { recursive: true });
  const entries = await readdir(src, { withFileTypes: true });
  
  for (const entry of entries) {
    const srcPath = join(src, entry.name);
    const destPath = join(dest, entry.name);
    
    if (entry.isDirectory()) {
      await copyDir(srcPath, destPath);
    } else {
      await copyFile(srcPath, destPath);
    }
  }
}

async function installSkill(skillName, targetDir) {
  const srcDir = join(SKILLS_DIR, skillName);
  const destDir = join(targetDir, skillName);
  
  try {
    await stat(join(srcDir, 'SKILL.md'));
  } catch {
    console.error(`  ❌ SKILL.md not found in ${skillName}`);
    return false;
  }
  
  try {
    // Remove existing if present
    if (existsSync(destDir)) {
      await rm(destDir, { recursive: true, force: true });
    }
    
    await copyDir(srcDir, destDir);
    return true;
  } catch (err) {
    console.error(`  ❌ Failed to install ${skillName}: ${err.message}`);
    return false;
  }
}

async function main() {
  const args = process.argv.slice(2);
  const specificSkill = args[0];
  
  console.log('📦 Installing skills...\n');
  
  // Get list of skills to install
  let skills;
  if (specificSkill) {
    skills = [specificSkill];
  } else {
    const entries = await readdir(SKILLS_DIR, { withFileTypes: true });
    skills = entries
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort();
  }
  
  if (skills.length === 0) {
    console.log('⚠️  No skills found to install');
    return;
  }
  
  // Install to each target directory
  for (const targetDir of TARGET_DIRS) {
    if (!existsSync(targetDir)) {
      console.log(`⏭️  Skipping ${targetDir} (does not exist)`);
      continue;
    }
    
    console.log(`📁 Installing to: ${targetDir}`);
    
    let installed = 0;
    for (const skill of skills) {
      const success = await installSkill(skill, targetDir);
      if (success) {
        console.log(`  ✅ ${skill}`);
        installed++;
      }
    }
    
    console.log(`  Installed ${installed}/${skills.length} skill(s)\n`);
  }
  
  console.log('✅ Done! Restart your AI coding tool to load the new skills.');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
