#!/usr/bin/env node

import { spawnSync } from 'child_process';
import { existsSync } from 'fs';
import { cp, rm } from 'fs/promises';
import { homedir } from 'os';
import { join } from 'path';

import { computeSkillHashes } from './lib/skill-hash.mjs';

const REPO_ROOT = process.cwd();
const MANIFEST_FILE = 'skills-manifest.json';
const DEFAULT_REMOTES = ['github', 'origin'];
const DEFAULT_BRANCH = 'master';
const REMOTE_LABELS = { github: 'GitHub', origin: 'Coding' };

// Directories where installed copies of skills are refreshed after --update.
// Only directories that already contain the skill are touched.
const INSTALL_TARGETS = [
  join(homedir(), '.codex', 'skills'),
  join(homedir(), '.claude', 'skills'),
  join(REPO_ROOT, '.agents', 'skills'),
  join(REPO_ROOT, '.claude', 'skills')
];

const STATUS_ICONS = {
  same: '✅',
  updated: '⬆️',
  new: '🆕',
  deleted: '🗑',
  conflict: '⚠️'
};

const STATUS_TEXT = {
  same: '本地==远端',
  updated: '远端有新内容',
  new: '远端新增',
  deleted: '远端已删除',
  conflict: '远端内容不一致'
};

function run(args, opts = {}) {
  return spawnSync(args[0], args.slice(1), {
    cwd: REPO_ROOT,
    encoding: 'utf8',
    ...opts
  });
}

function remoteLabel(remote) {
  return REMOTE_LABELS[remote] || remote;
}

function parseArgs(argv) {
  const opts = { update: false, remotes: [], branch: DEFAULT_BRANCH };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--update') {
      opts.update = true;
    } else if (arg === '--remote') {
      i++;
      if (i >= argv.length) {
        throw new Error('--remote requires a remote name');
      }
      opts.remotes.push(
        ...argv[i]
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean)
      );
    } else if (arg === '--branch') {
      i++;
      if (i >= argv.length) {
        throw new Error('--branch requires a branch name');
      }
      opts.branch = argv[i];
    } else {
      throw new Error(`Unknown argument: ${arg}`);
    }
  }

  if (opts.remotes.length === 0) {
    opts.remotes = [...DEFAULT_REMOTES];
  }
  return opts;
}

function fetchRemote(remote) {
  const res = run(['git', 'fetch', remote]);
  if (res.status !== 0) {
    return { ok: false, error: (res.stderr || res.stdout || '').trim() };
  }
  return { ok: true };
}

function readRemoteManifest(remote, branch) {
  const res = run(['git', 'show', `${remote}/${branch}:${MANIFEST_FILE}`]);
  if (res.status !== 0) {
    return {
      ok: false,
      missing: true,
      error: (res.stderr || res.stdout || '').trim()
    };
  }
  try {
    return { ok: true, manifest: JSON.parse(res.stdout) };
  } catch (err) {
    return { ok: false, missing: false, error: `invalid JSON: ${err.message}` };
  }
}

/**
 * Classify a skill from the records produced by reachable remotes.
 */
function classifySkill(records) {
  let same = 0;
  let deleted = 0;
  let newCount = 0;
  const updatedHashes = new Set();

  for (const record of records) {
    if (record.status === 'same') same++;
    else if (record.status === 'deleted') deleted++;
    else if (record.status === 'new') newCount++;
    else if (record.status === 'updated') updatedHashes.add(record.hash);
  }

  const total = records.length;

  if (updatedHashes.size > 1) {
    return { final: 'conflict', updateHash: null };
  }

  if (updatedHashes.size === 1) {
    if (deleted > 0 || same > 0 || newCount > 0) {
      return { final: 'conflict', updateHash: null };
    }
    return { final: 'updated', updateHash: [...updatedHashes][0] };
  }

  if (deleted > 0) {
    if (deleted === total) {
      return { final: 'deleted', updateHash: null };
    }
    return { final: 'conflict', updateHash: null };
  }

  if (newCount > 0) {
    if (newCount === total) {
      return { final: 'new', updateHash: records[0].hash };
    }
    return { final: 'conflict', updateHash: null };
  }

  if (same === total) {
    return { final: 'same', updateHash: null };
  }

  return { final: 'conflict', updateHash: null };
}

async function reinstallSkill(name) {
  const src = join(REPO_ROOT, 'skills', name);
  if (!existsSync(src)) {
    console.error(`   ❌ ${name}: 源目录不存在，跳过安装刷新`);
    return;
  }

  for (const target of INSTALL_TARGETS) {
    if (!existsSync(target)) {
      continue;
    }
    const dest = join(target, name);
    // Only refresh directories that already contain this skill.
    if (!existsSync(dest)) {
      continue;
    }
    try {
      await rm(dest, { recursive: true, force: true });
      await cp(src, dest, { recursive: true });
      console.log(`   📁 已刷新 ${dest}`);
    } catch (err) {
      console.error(`   ❌ 刷新 ${dest} 失败: ${err.message}`);
    }
  }
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const branch = opts.branch;

  console.log(`🔍 检查更新 (branch: ${branch}, remotes: ${opts.remotes.join(', ')})`);

  // 1. Compute local hashes.
  const localSkills = await computeSkillHashes(REPO_ROOT);
  console.log(`  本地 ${Object.keys(localSkills).length} 个 skill\n`);

  // 2. Fetch remotes and read their manifests.
  const remoteErrors = [];
  const remoteManifests = new Map();

  for (const remote of opts.remotes) {
    const fetchResult = fetchRemote(remote);
    if (!fetchResult.ok) {
      console.log(`⚠️  无法访问远端 ${remoteLabel(remote)}: ${fetchResult.error}`);
      remoteErrors.push(remote);
      continue;
    }
    console.log(`✔ 已获取远端 ${remoteLabel(remote)}`);

    const manifestResult = readRemoteManifest(remote, branch);
    if (!manifestResult.ok) {
      const reason = manifestResult.missing
        ? `分支 ${remote}/${branch} 中缺少 ${MANIFEST_FILE}`
        : manifestResult.error;
      console.log(`⚠️  ${remoteLabel(remote)}: ${reason}`);
      remoteErrors.push(remote);
      continue;
    }
    remoteManifests.set(remote, manifestResult.manifest.skills || {});
  }

  console.log('');

  if (remoteManifests.size === 0) {
    console.error('❌ 没有任何远端提供了有效的清单，无法比较。');
    process.exit(2);
  }

  // 3. Compare per skill.
  const allNames = new Set([
    ...Object.keys(localSkills),
    ...[...remoteManifests.values()].flatMap((m) => Object.keys(m))
  ]);

  const summary = [];
  for (const name of [...allNames].sort()) {
    const records = [];
    for (const [remote, remoteSkills] of remoteManifests) {
      const localHash = localSkills[name]?.hash;
      const remoteHash = remoteSkills[name]?.hash;
      let status;
      let hash = remoteHash || null;
      if (!remoteHash) {
        status = 'deleted';
      } else if (!localHash) {
        status = 'new';
      } else if (localHash === remoteHash) {
        status = 'same';
      } else {
        status = 'updated';
      }
      records.push({ remote, status, hash });
    }

    const { final, updateHash } = classifySkill(records);
    summary.push({
      name,
      final,
      updateHash,
      records,
      remotes: records.map((r) => remoteLabel(r.remote))
    });
  }

  // 4. Report.
  const counts = { same: 0, updated: 0, new: 0, deleted: 0, conflict: 0 };
  console.log('📊 状态汇总:');
  for (const skill of summary) {
    counts[skill.final]++;
    const labels = [...new Set(skill.remotes)].join(', ');
    console.log(
      `  ${STATUS_ICONS[skill.final]} ${skill.name}  (${STATUS_TEXT[skill.final]})  [${labels}]`
    );
  }

  console.log(
    `\n  共 ${summary.length} 个 skill：` +
      `✅ ${counts.same}，⬆️ ${counts.updated}，🆕 ${counts.new}，` +
      `🗑 ${counts.deleted}，⚠️ ${counts.conflict}`
  );

  const updatesAvailable = summary.some((s) =>
    ['updated', 'new', 'deleted', 'conflict'].includes(s.final)
  );

  const applied = [];
  const skipped = [];

  // 5. Apply updates.
  if (opts.update) {
    console.log('\n⬇️  应用远端更新...');
    for (const skill of summary) {
      if (skill.final === 'conflict') {
        console.log(`⏭️  ${skill.name}: 跳过（远端内容不一致，请手动处理）`);
        skipped.push(skill.name);
        continue;
      }
      if (skill.final === 'deleted') {
        console.log(`⏭️  ${skill.name}: 远端已删除，不执行删除操作`);
        continue;
      }
      if (skill.final !== 'updated' && skill.final !== 'new') {
        continue;
      }

      const rel = `skills/${skill.name}`;

      // Safety rule: skip skills with uncommitted local changes.
      const status = run([
        'git',
        'status',
        '--porcelain',
        '--untracked-files=all',
        '--',
        rel
      ]);
      if ((status.stdout || '').trim()) {
        console.log(`⏭️  ${skill.name}: 跳过（本地存在未提交修改）`);
        skipped.push(skill.name);
        continue;
      }

      const sourceRemote = skill.records.find((r) => {
        if (skill.final === 'new') {
          return r.status === 'new';
        }
        return r.status === 'updated' && r.hash === skill.updateHash;
      })?.remote;

      if (!sourceRemote) {
        console.log(`⏭️  ${skill.name}: 跳过（找不到一致的远端来源）`);
        skipped.push(skill.name);
        continue;
      }

      const ref = `${sourceRemote}/${branch}`;
      const restore = run([
        'git',
        'restore',
        `--source=${ref}`,
        '--worktree',
        '--',
        rel
      ]);

      if (restore.status !== 0) {
        console.error(
          `❌ ${skill.name}: 更新失败: ${(restore.stderr || restore.stdout || '').trim()}`
        );
        skipped.push(skill.name);
        continue;
      }

      console.log(`✅ ${skill.name}: 已同步 ${sourceRemote}/${branch}`);
      applied.push(skill.name);
      await reinstallSkill(skill.name);
    }

    // 6. Regenerate the local manifest so it matches the updated worktree
    // (the file is left uncommitted for the user to review), then validate.
    if (applied.length > 0) {
      console.log('\n📋 重新生成 skills-manifest.json...');
      const manifest = run([
        process.execPath,
        join(REPO_ROOT, 'scripts', 'generate-manifest.mjs')
      ]);
      if (manifest.status !== 0) {
        console.error('❌ 重新生成 skills-manifest.json 失败。');
        process.exit(2);
      }
    }

    if (applied.length > 0) {
      console.log('\n🔍 运行 npm run validate...');
      const validate = run(
        [process.execPath, join(REPO_ROOT, 'scripts', 'validate.mjs')],
        { stdio: 'inherit' }
      );
      if (validate.status !== 0) {
        console.error('❌ 更新后验证失败。');
        process.exit(2);
      }
    }

    console.log(
      applied.length
        ? `\n✅ 已更新 ${applied.length} 个 skill: ${applied.join(', ')}`
        : '\n✅ 本次没有应用任何更新'
    );
    if (skipped.length) {
      console.log(`⏭️  跳过 ${skipped.length} 个 skill: ${skipped.join(', ')}`);
    }
  }

  // 7. Exit code.
  if (remoteErrors.length > 0) {
    console.error(
      `\n❌ ${remoteErrors.length} 个远端不可用或无清单 (${remoteErrors.join(', ')})`
    );
    process.exit(2);
  }

  if (opts.update) {
    const stillPending = summary.some((s) => {
      if (s.final === 'deleted') return true;
      if (s.final === 'conflict') return true;
      if (s.final === 'updated' || s.final === 'new') {
        return !applied.includes(s.name);
      }
      return false;
    });
    process.exit(stillPending ? 1 : 0);
  }

  process.exit(updatesAvailable ? 1 : 0);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(2);
});
