#!/usr/bin/env node

import { readFileSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const packageJson = JSON.parse(readFileSync(join(__dirname, '..', 'package.json'), 'utf-8'));

const args = process.argv.slice(2);
const command = args[0];

function showHelp() {
  console.log(`
seahi-skills v${packageJson.version}

Usage: seahi-skills <command>

Commands:
  list              List all available skills
  version           Show current version
  help              Show this help message

Examples:
  seahi-skills list
  seahi-skills version
`);
}

function listSkills() {
  const skillsDir = join(__dirname, '..', 'skills');
  
  console.log('Available skills:\n');
  
  try {
    const entries = readdirSync(skillsDir, { withFileTypes: true });
    const skills = entries
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort();
    
    if (skills.length === 0) {
      console.log('  No skills found');
      return;
    }
    
    for (const skill of skills) {
      console.log(`  - ${skill}`);
    }
    console.log(`\nTotal: ${skills.length} skill(s)`);
  } catch (err) {
    console.error('Error reading skills directory:', err.message);
  }
}

function showVersion() {
  console.log(packageJson.version);
}

switch (command) {
  case 'list':
    listSkills();
    break;
  case 'version':
    showVersion();
    break;
  case 'help':
  case undefined:
    showHelp();
    break;
  default:
    console.error(`Unknown command: ${command}`);
    showHelp();
    process.exit(1);
}
