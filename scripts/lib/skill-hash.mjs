#!/usr/bin/env node

import { createHash } from 'crypto';
import { spawnSync } from 'child_process';
import { readFile } from 'fs/promises';
import { join } from 'path';

const SKILLS_REL = 'skills';

/**
 * Compute the SHA-256 hex digest of a buffer.
 */
export function sha256(input) {
  return createHash('sha256').update(input).digest('hex');
}

/**
 * Normalize content before hashing so results are identical on every
 * platform, regardless of Git's autocrlf handling. Binary files (containing
 * a NUL byte) are hashed as-is.
 */
export function normalizeContent(buf) {
  if (buf.includes(0)) {
    return buf;
  }
  return Buffer.from(buf.toString('utf8').replace(/\r\n/g, '\n'), 'utf8');
}

/**
 * Read a file and return its deterministic hash and normalized size.
 */
export async function fileSha256(absPath) {
  const raw = await readFile(absPath);
  const normalized = normalizeContent(raw);
  return { hash: sha256(normalized), size: normalized.length };
}

/**
 * Return a map of skill name -> sorted list of tracked files (POSIX relative
 * paths inside the skill directory). Only top-level directories under
 * skills/ that contain a tracked SKILL.md are considered skills, matching
 * the rule used by scripts/build.mjs. The list combines tracked files with
 * untracked files that are not gitignored, so brand-new skills are covered
 * even before they are staged. Gitignored files (local scratch files) are
 * excluded so the manifest always matches what Git would commit.
 */
export function trackedSkillFiles(repoRoot) {
  const res = spawnSync(
    'git',
    ['ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', SKILLS_REL],
    { cwd: repoRoot, encoding: 'utf8' }
  );

  if (res.status !== 0) {
    throw new Error(
      `git ls-files failed (status ${res.status}): ${(res.stderr || res.stdout || '').trim()}`
    );
  }

  const bySkill = new Map();
  for (const file of res.stdout.split('\0').filter(Boolean)) {
    const match = /^skills\/([^/]+)\/(.+)$/.exec(file);
    if (!match) {
      continue;
    }
    const [, name, rest] = match;
    if (!bySkill.has(name)) {
      bySkill.set(name, []);
    }
    bySkill.get(name).push(rest);
  }

  const result = {};
  for (const name of [...bySkill.keys()].sort()) {
    const files = bySkill.get(name);
    if (files.includes('SKILL.md')) {
      result[name] = files.sort();
    }
  }
  return result;
}

/**
 * Compute deterministic hashes for every tracked skill.
 *
 * Skill hash = SHA-256 over lines of `relativePath\0fileHash\n` for each
 * file, sorted by POSIX relative path.
 */
export async function computeSkillHashes(repoRoot) {
  const tracked = trackedSkillFiles(repoRoot);
  const skills = {};

  for (const name of Object.keys(tracked).sort()) {
    const skillDir = join(repoRoot, SKILLS_REL, name);
    const parts = [];
    let totalSize = 0;

    for (const rel of tracked[name]) {
      const { hash, size } = await fileSha256(join(skillDir, rel));
      totalSize += size;
      parts.push(`${rel}\0${hash}\n`);
    }

    skills[name] = {
      hash: sha256(Buffer.from(parts.join(''), 'utf8')),
      files: tracked[name].length,
      size: totalSize
    };
  }

  return skills;
}

/**
 * Build the deterministic manifest object. No timestamps or absolute paths.
 */
export function buildManifest(skills) {
  return { schemaVersion: 1, skills };
}

/**
 * Serialize a manifest for writing (stable, sorted keys, trailing newline).
 */
export function manifestJson(manifest) {
  return `${JSON.stringify(manifest, null, 2)}\n`;
}
