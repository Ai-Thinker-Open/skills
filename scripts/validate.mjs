#!/usr/bin/env node

import { readdir, readFile, stat } from 'fs/promises';
import { join, relative } from 'path';

const SKILLS_DIR = join(process.cwd(), 'skills');

async function findSkillFiles(dir) {
  const results = [];
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        results.push(...await findSkillFiles(fullPath));
      } else if (entry.name === 'SKILL.md') {
        results.push(fullPath);
      }
    }
  } catch (err) {
    // Directory doesn't exist or can't be read
  }
  return results;
}

async function validateFrontmatter(filePath) {
  const content = await readFile(filePath, 'utf-8');
  const lines = content.split('\n');
  
  // Check for frontmatter
  if (!lines[0]?.trim().startsWith('---')) {
    return { valid: false, error: 'Missing frontmatter (must start with ---)' };
  }
  
  // Find end of frontmatter
  let endIndex = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === '---') {
      endIndex = i;
      break;
    }
  }
  
  if (endIndex === -1) {
    return { valid: false, error: 'Unterminated frontmatter' };
  }
  
  const frontmatter = lines.slice(1, endIndex).join('\n');
  
  // Check for required fields
  if (!frontmatter.includes('name:')) {
    return { valid: false, error: 'Missing required field: name' };
  }
  
  if (!frontmatter.includes('description:')) {
    return { valid: false, error: 'Missing required field: description' };
  }
  
  // Validate name format (lowercase, hyphens only)
  const nameMatch = frontmatter.match(/name:\s*(.+)/);
  if (nameMatch) {
    const name = nameMatch[1].trim();
    if (!/^[a-z0-9-]+$/.test(name)) {
      return { valid: false, error: `Invalid name format: "${name}" (must be lowercase with hyphens only)` };
    }
  }
  
  return { valid: true };
}

async function main() {
  console.log('🔍 Validating skills...\n');
  
  const skillFiles = await findSkillFiles(SKILLS_DIR);
  
  if (skillFiles.length === 0) {
    console.log('⚠️  No SKILL.md files found in skills/ directory');
    process.exit(0);
  }
  
  let hasErrors = false;
  
  for (const file of skillFiles) {
    const relativePath = relative(process.cwd(), file);
    const result = await validateFrontmatter(file);
    
    if (result.valid) {
      console.log(`✅ ${relativePath}`);
    } else {
      console.log(`❌ ${relativePath}`);
      console.log(`   Error: ${result.error}`);
      hasErrors = true;
    }
  }
  
  console.log(`\n📊 Found ${skillFiles.length} skill(s)`);
  
  if (hasErrors) {
    console.log('\n❌ Validation failed');
    process.exit(1);
  } else {
    console.log('\n✅ All skills are valid');
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
