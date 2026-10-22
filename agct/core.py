"""Project-local task memory, exact checkpoints and conditional experience.

Records describe saved evidence, never business acceptance or model internals.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
import stat
import subprocess
import uuid

from .store import Store, GovernanceError, now

MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_CHECKPOINT_BYTES = 128 * 1024 * 1024
MAX_PATHS = 500


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _linked(path):
    if path.is_symlink():
        return True
    try:
        return bool(getattr(path.lstat(), 'st_file_attributes', 0) & 0x400)
    except FileNotFoundError:
        return False


def validate_relative_path(root, value, allow_missing=True):
    if not isinstance(value, str) or not value or '\x00' in value or '\\' in value:
        raise GovernanceError('UNSAFE_PATH', 'Use an explicit relative path with forward slashes.')
    relative = PurePosixPath(value)
    if relative.is_absolute() or PureWindowsPath(value).drive or any(p in ('..', '.') for p in value.split('/')):
        raise GovernanceError('UNSAFE_PATH', 'Absolute paths and parent traversal are not allowed.')
    for part in relative.parts:
        low = part.casefold()
        if re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', low):
            raise GovernanceError('UNSAFE_PATH', 'Reserved device filenames are not portable file paths.')
        if low in ('.git', '.agct') or ':' in part or part.endswith((' ', '.')):
            raise GovernanceError('RESERVED_PATH', 'Repository and governance metadata cannot be captured.')
        if (low in ('.env', 'credentials', 'credentials.json', 'id_rsa', 'id_ed25519')
                or low.startswith('.env.') and low not in ('.env.example', '.env.sample', '.env.template')
                or low.endswith(('.pfx', '.p12', '.key', '.pem'))):
            raise GovernanceError('SECRET_PATH', 'This filename may contain credentials; it is excluded by default.')
    root = Path(root).resolve()
    candidate = root.joinpath(*relative.parts)
    check = root
    for part in relative.parts:
        check = check / part
        if _linked(check):
            raise GovernanceError('SYMLINK_PATH', 'Symbolic links and junctions cannot be captured.')
    if not candidate.resolve().is_relative_to(root):
        raise GovernanceError('UNSAFE_PATH', 'The path resolves outside its workspace.')
    if candidate.exists() and not candidate.is_file():
        raise GovernanceError('NOT_FILE', 'Checkpoint paths must name individual regular files.')
    if not allow_missing and not candidate.is_file():
        raise GovernanceError('MISSING_FILE', 'The requested file does not exist.', {'path': value})
    return candidate


def read_file_bytes(path, max_bytes=MAX_FILE_BYTES):
    path = Path(path)
    if _linked(path):
        raise GovernanceError('SYMLINK_PATH', 'Symbolic links and junctions are not supported.')
    before = path.stat()
    if not stat.S_ISREG(before.st_mode):
        raise GovernanceError('NOT_FILE', 'Only regular files can be read.')
    if before.st_size > max_bytes:
        raise GovernanceError('FILE_TOO_LARGE', 'Use an artifact reference for files exceeding the snapshot limit.')
    with path.open('rb') as stream:
        content = stream.read(max_bytes + 1)
    after = path.stat()
    if len(content) > max_bytes or (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise GovernanceError('SOURCE_CHANGED', 'The file changed during capture; no checkpoint was published.')
    return content


def git(root, *args, input_bytes=None, check=True):
    environment = os.environ.copy()
    for key in list(environment):
        if key.startswith('GIT_'):
            environment.pop(key)
    environment.update(GIT_TERMINAL_PROMPT='0', GIT_OPTIONAL_LOCKS='0', GIT_CONFIG_NOSYSTEM='1')
    try:
        result = subprocess.run(['git', '--literal-pathspecs', '-c', 'core.hooksPath=' + os.devnull, '-c', 'core.autocrlf=false', '-c', 'commit.gpgSign=false', '-C', str(root), *args],
                                input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                env=environment, timeout=60, check=False)
    except FileNotFoundError as exc:
        raise GovernanceError('GIT_UNAVAILABLE', 'Git is required for this operation.') from exc
    except subprocess.TimeoutExpired as exc:
        raise GovernanceError('GIT_TIMEOUT', 'The bounded Git operation timed out.') from exc
    if check and result.returncode:
        raise GovernanceError('GIT_ERROR', 'Git could not complete the operation.',
                              {'command': args[0] if args else '', 'stderr': result.stderr.decode('utf-8', 'replace')[:2000]})
    return result


def _id(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,99}', value):
        raise GovernanceError('INVALID_ID', f'{label} must be 1-100 ASCII letters, digits, dots, underscores or hyphens.')
    return value


class Core:
    def __init__(self, project):
        self.store = Store(project)
        self.root = self.store.root
        config = self.store.get('config', 'project')
        if not config or config.get('schema_version') != 1:
            raise GovernanceError('SCHEMA_VERSION_UNSUPPORTED', 'Use a compatible toolkit version for this project state.')

    @classmethod
    def initialize(cls, project, name='Agent Co-Governance Toolkit project'):
        store = Store(project, create=True)
        with store.guard():
            config = store.get('config', 'project')
            if config is not None and config.get('schema_version') != 1:
                raise GovernanceError('SCHEMA_VERSION_UNSUPPORTED', 'Initialization cannot downgrade existing project state.')
            if config is None:
                config = {'name': name, 'schema_version': 1, 'created_at': now(), 'synthetic': False}
                store.put('config', 'project', config)
                store.put('experience', 'receipt-recovery-v1', {
                    'rule_id': 'receipt-recovery-v1', 'code': 'EFFECT_PRESENT_RECEIPT_MISSING',
                    'operation': 'reconcile', 'action': 'verify_and_finalize', 'task_id': None,
                    'version': '1', 'enabled': True, 'updated_at': now()})
                store.event('project_initialized', {'name': name})
        return {'initialized': True, 'project': str(store.root), 'config': config}

    def _task(self, task_id):
        task = self.store.get('tasks', _id(task_id, 'Task ID'))
        if task is None:
            raise GovernanceError('TASK_NOT_FOUND', 'Create the task before capturing or delivering work.', {'task_id': task_id})
        return task

    def task(self, task_id, title=None, workstream=None, state=None):
        task_id = _id(task_id, 'Task ID')
        if state is not None and state not in ('active', 'paused', 'waiting', 'complete'):
            raise GovernanceError('INVALID_STATE', 'Task state must be active, paused, waiting or complete.')
        with self.store.guard():
            previous = self.store.get('tasks', task_id)
            result = dict(previous or {'task_id': task_id, 'title': title or task_id, 'workstream': workstream or task_id,
                                       'state': 'active', 'created_at': now()})
            for key, value in (('title', title), ('workstream', workstream), ('state', state)):
                if value is not None:
                    result[key] = value
            if result != previous:
                result['updated_at'] = now()
                self.store.put('tasks', task_id, result)
                self.store.event('task_changed', result)
            return result

    def status(self):
        tasks, stages, operations, workspaces = (self.store.list(x) for x in ('tasks', 'stages', 'operations', 'workspaces'))
        terminal = {'accepted', 'committed', 'complete', 'completed', 'superseded', 'cancelled', 'dismissed', 'finalized', 'adopted'}
        pending_stages = [s for s in stages if str(s.get('state', s.get('status', 'queued'))).lower() not in terminal]
        # Submission validates cumulative ancestry. Project that declaration here
        # without pretending that the older stage already has a terminal receipt.
        stage_index = {s.get('stage_id'): s for s in stages if s.get('stage_id')}
        covered_pending = {}
        for successor in stages:
            if (str(successor.get('status', successor.get('state', ''))).lower() not in ('queued', 'conflict')
                    or successor.get('relation') != 'cumulative'
                    or not successor.get('task_id') or not successor.get('workspace')
                    or not successor.get('stage_id')):
                continue
            remaining, visited = list(successor.get('supersedes', [])), {successor['stage_id']}
            while remaining:
                old_id = remaining.pop()
                if old_id in visited:
                    continue
                visited.add(old_id)
                old = stage_index.get(old_id)
                if not old or old.get('task_id') != successor['task_id'] or old.get('workspace') != successor['workspace']:
                    continue
                if str(old.get('status', old.get('state', ''))).lower() == 'queued':
                    covered_pending[old_id] = successor['stage_id']
                if old.get('relation') == 'cumulative':
                    remaining.extend(old.get('supersedes', []))
        pending_stages = [s for s in pending_stages if s.get('stage_id') not in covered_pending]
        pending_operations = [o for o in operations if str(o.get('state', o.get('status', 'pending'))).lower() not in terminal]
        artifacts = self.store.list('artifacts')
        return {'tasks': tasks, 'stages': stages, 'operations': operations, 'workspaces': workspaces,
                'actionable': {'stages': pending_stages, 'operations': pending_operations,
                               'artifacts': [a for a in artifacts if a.get('decision') not in ('ignore', 'dismiss', 'no_backup_needed') and not a.get('backup_verified')]},
                'retained_task_state': [t for t in tasks if t['state'] in ('paused', 'waiting')],
                'covered_pending_stages': [{'stage_id': sid, 'awaiting_successor': successor}
                                           for sid, successor in sorted(covered_pending.items())],
                'checkpoints': self.store.list('checkpoints'), 'artifacts': artifacts,
                'history_counts': {'terminal_stages': sum(str(s.get('state', s.get('status', 'queued'))).lower() in terminal for s in stages),
                                   'terminal_operations': len(operations) - len(pending_operations)},
                'meaning': 'Task state and checkpoint retention do not create a delivery obligation or imply business acceptance.'}

    def _snapshot(self, data):
        digest = digest_bytes(data)
        directory = self.store.directory / 'objects'
        if _linked(directory):
            raise GovernanceError('UNSAFE_METADATA', 'Snapshot storage cannot be a symbolic link.')
        directory.mkdir(exist_ok=True)
        target = directory / digest
        if target.exists():
            if digest_bytes(read_file_bytes(target)) != digest:
                raise GovernanceError('SNAPSHOT_CORRUPT', 'An existing immutable snapshot failed verification.')
        else:
            try:
                with target.open('xb') as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
            except FileExistsError:
                if digest_bytes(read_file_bytes(target)) != digest:
                    raise GovernanceError('SNAPSHOT_CORRUPT', 'A concurrent snapshot failed verification.')
        return {'sha256': digest, 'size': len(data)}

    def _blob(self, workspace, oid, mode):
        if mode not in ('100644', '100755'):
            raise GovernanceError('UNSUPPORTED_GIT_ENTRY', 'Links, submodules, directories and unmerged entries are not checkpoint files.')
        size = int(git(workspace, 'cat-file', '-s', oid).stdout.strip())
        if size > MAX_FILE_BYTES:
            raise GovernanceError('FILE_TOO_LARGE', 'A Git blob exceeds the checkpoint file limit.')
        data = git(workspace, 'cat-file', 'blob', oid).stdout
        return {**self._snapshot(data), 'mode': mode, 'git_oid': oid}

    def checkpoint(self, task_id, workspace, paths, next_step, decision='', paused=False):
        if (not isinstance(paths, list) or not paths or len(paths) > MAX_PATHS
                or any(not isinstance(p, str) for p in paths)
                or len({p.casefold() for p in paths}) != len(paths)):
            raise GovernanceError('INVALID_PATHS', 'Provide 1-500 unique explicit file paths.')
        raw_workspace = Path(workspace).expanduser().absolute()
        if any(_linked(p) for p in (raw_workspace, *raw_workspace.parents)):
            raise GovernanceError('SYMLINK_PATH', 'Workspace cannot traverse symbolic links or junctions.')
        workspace = raw_workspace.resolve()
        if not workspace.is_dir():
            raise GovernanceError('MISSING_WORKSPACE', 'The source workspace does not exist.')
        for path in paths:
            validate_relative_path(workspace, path)
        with self.store.guard():
            task = self._task(task_id)
            is_git = git(workspace, 'rev-parse', '--is-inside-work-tree', check=False).returncode == 0
            if is_git and Path(git(workspace, 'rev-parse', '--show-toplevel').stdout.decode().strip()).resolve() != workspace:
                raise GovernanceError('GIT_WORKSPACE_ROOT', 'Use the Git worktree root and paths relative to that root.')
            head = git(workspace, 'rev-parse', '--verify', 'HEAD', check=False).stdout.decode().strip() if is_git else None
            index_before = git(workspace, 'ls-files', '--stage', '-z', '--', *paths).stdout if is_git else b''
            files, total = [], 0
            index = {}
            for entry in index_before.split(b'\x00'):
                if not entry:
                    continue
                metadata, encoded_path = entry.split(b'\t', 1)
                mode, oid, stage = metadata.decode().split()
                if stage != '0':
                    raise GovernanceError('UNMERGED_INDEX', 'Resolve or separately preserve merge-conflict stages before checkpointing.')
                index[encoded_path.decode('utf-8')] = (mode, oid)
            for path in paths:
                source = validate_relative_path(workspace, path)
                record = {'path': path, 'head': None, 'index': None, 'worktree': None}
                if is_git and head:
                    entry = git(workspace, 'ls-tree', '-z', head, '--', path).stdout.rstrip(b'\x00')
                    if entry:
                        meta, _ = entry.split(b'\t', 1)
                        mode, kind, oid = meta.decode().split()
                        record['head'] = self._blob(workspace, oid, mode)
                if path in index:
                    mode, oid = index[path]
                    record['index'] = self._blob(workspace, oid, mode)
                if source.exists():
                    data = read_file_bytes(source)
                    record['worktree'] = {**self._snapshot(data), 'mode': '100755' if source.stat().st_mode & stat.S_IXUSR else '100644'}
                if all(record[layer] is None for layer in ('head', 'index', 'worktree')):
                    raise GovernanceError('MISSING_FILE', 'A selected path has no Git or filesystem content.', {'path': path})
                total += sum(record[layer]['size'] for layer in ('head', 'index', 'worktree') if record[layer])
                if total > MAX_CHECKPOINT_BYTES:
                    raise GovernanceError('CHECKPOINT_TOO_LARGE', 'The checkpoint exceeds its total snapshot limit.')
                files.append(record)
            if is_git:
                if index_before != git(workspace, 'ls-files', '--stage', '-z', '--', *paths).stdout or head != git(workspace, 'rev-parse', '--verify', 'HEAD', check=False).stdout.decode().strip():
                    raise GovernanceError('SOURCE_CHANGED', 'Git HEAD or selected index entries changed during capture.')
            for record in files:
                source = validate_relative_path(workspace, record['path'])
                frozen = record['worktree']
                if (source.exists() != (frozen is not None)) or (frozen and digest_bytes(read_file_bytes(source)) != frozen['sha256']):
                    raise GovernanceError('SOURCE_CHANGED', 'A selected worktree file changed during capture.')
            checkpoint_id = 'cp-' + uuid.uuid4().hex
            result = {'checkpoint_id': checkpoint_id, 'task_id': task_id, 'workspace': str(workspace),
                      'git': is_git, 'original_head': head or None, 'files': files, 'next_step': next_step,
                      'decision': decision, 'created_at': now(), 'scope': 'selected_files_only',
                      'delivery': False, 'total_layer_bytes': total}
            self.store.put('checkpoints', checkpoint_id, result)
            task.update(latest_checkpoint=checkpoint_id, next_step=next_step, updated_at=now())
            if paused:
                task['state'] = 'paused'
            self.store.put('tasks', task_id, task)
            self.store.event('checkpoint_saved', {'checkpoint_id': checkpoint_id, 'task_id': task_id})
            return result

    def _snapshot_bytes(self, reference):
        digest = reference.get('sha256', '')
        if not re.fullmatch(r'[0-9a-f]{64}', digest):
            raise GovernanceError('SNAPSHOT_CORRUPT', 'Invalid snapshot object identity.')
        source = self.store.directory / 'objects' / digest
        if _linked(source.parent) or _linked(source) or not source.is_file():
            raise GovernanceError('SNAPSHOT_CORRUPT', 'Snapshot object is missing or unsafe.')
        data = read_file_bytes(source)
        if digest_bytes(data) != digest or len(data) != reference['size']:
            raise GovernanceError('SNAPSHOT_CORRUPT', 'Snapshot digest or size verification failed.')
        return data

    def restore(self, checkpoint_id, destination):
        with self.store.guard():
            checkpoint = self.store.get('checkpoints', checkpoint_id)
            if checkpoint is None:
                raise GovernanceError('CHECKPOINT_NOT_FOUND', 'The checkpoint does not exist.')
            raw = Path(destination).expanduser().absolute()
            for ancestor in (raw, *raw.parents):
                if _linked(ancestor):
                    raise GovernanceError('SYMLINK_PATH', 'Restore destination cannot traverse symbolic links or junctions.')
            destination = raw.resolve()
            source = Path(checkpoint['workspace']).resolve()
            if destination == self.root or destination.is_relative_to(self.root) or self.root.is_relative_to(destination) or destination == source or destination.is_relative_to(source) or source.is_relative_to(destination):
                raise GovernanceError('RESTORE_NOT_INDEPENDENT', 'Restore into an independent directory outside source and governance workspaces.')
            if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
                raise GovernanceError('RESTORE_NOT_EMPTY', 'Restore destination must be absent or empty.')
            # Validate every object before creating or writing the destination.
            contents = {}
            for record in checkpoint['files']:
                validate_relative_path(destination, record['path'])
                for layer in ('head', 'index', 'worktree'):
                    if record[layer]:
                        contents[(record['path'], layer)] = self._snapshot_bytes(record[layer])
            destination.mkdir(parents=True, exist_ok=True)
            if checkpoint['git']:
                git(destination, 'init', '--quiet')
                git(destination, 'config', 'user.name', 'AGCT synthetic restore')
                git(destination, 'config', 'user.email', 'restore@example.invalid')
                for record in checkpoint['files']:
                    if record['head']:
                        data = contents[(record['path'], 'head')]
                        oid = git(destination, 'hash-object', '-w', '--stdin', input_bytes=data).stdout.decode().strip()
                        git(destination, 'update-index', '--add', '--cacheinfo', record['head']['mode'], oid, record['path'])
                git(destination, 'commit', '--allow-empty', '--quiet', '-m',
                    'AGCT synthetic restore baseline; original HEAD: ' + str(checkpoint['original_head']))
                for record in checkpoint['files']:
                    if record['index']:
                        oid = git(destination, 'hash-object', '-w', '--stdin', input_bytes=contents[(record['path'], 'index')]).stdout.decode().strip()
                        git(destination, 'update-index', '--add', '--cacheinfo', record['index']['mode'], oid, record['path'])
                    else:
                        git(destination, 'update-index', '--force-remove', '--', record['path'])
            for record in checkpoint['files']:
                if record['worktree']:
                    target = destination / record['path']
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(contents[(record['path'], 'worktree')])
                    if os.name != 'nt':
                        target.chmod(0o755 if record['worktree']['mode'] == '100755' else 0o644)
            result = {'checkpoint_id': checkpoint_id, 'destination': str(destination), 'restored': True,
                      'synthetic_git_baseline': checkpoint['git'], 'original_head': checkpoint['original_head'],
                      'scope': 'selected_files_only', 'original_workspace_modified': False}
            self.store.event('checkpoint_restored', result)
            return result

    def artifact(self, task_id, path, role='input', backup=None, decision=None):
        if decision not in (None, 'ignore', 'dismiss', 'no_backup_needed', 'retain'):
            raise GovernanceError('INVALID_DECISION', 'Artifact decision must be ignore, dismiss, no_backup_needed or retain.')
        self._task(task_id)
        raw = Path(path).expanduser().absolute()
        if any(part.casefold() in ('.git', '.agct') for part in raw.parts):
            raise GovernanceError('RESERVED_PATH', 'Git and governance metadata cannot become artifacts.')
        # Artifact reads are explicitly named, but metadata/secret/link exclusions still apply.
        for ancestor in (raw, *raw.parents):
            if _linked(ancestor):
                raise GovernanceError('SYMLINK_PATH', 'Artifact paths cannot traverse symbolic links or junctions.')
        validate_relative_path(raw.parent, raw.name, allow_missing=False)
        digest = hashlib.sha256()
        before = raw.stat()
        with raw.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
        after = raw.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise GovernanceError('SOURCE_CHANGED', 'The artifact changed during hashing.')
        checksum = digest.hexdigest()
        artifact_id = 'ar-' + digest_bytes((task_id + '\x00' + str(raw.resolve())).encode())[:32]
        old = self.store.get('artifacts', artifact_id)
        if backup is None and old and old['sha256'] == checksum:
            backup = old.get('backup')
        verified = False
        backup_path = None
        if backup is not None:
            backup_path = Path(backup).expanduser().absolute()
            if backup_path.resolve() == raw.resolve() or backup_path.exists() and os.path.samefile(backup_path, raw):
                raise GovernanceError('BACKUP_NOT_INDEPENDENT', 'The original file is not an independent backup.')
            for ancestor in (backup_path, *backup_path.parents):
                if _linked(ancestor):
                    raise GovernanceError('SYMLINK_PATH', 'Backup paths cannot traverse symbolic links or junctions.')
            validate_relative_path(backup_path.parent, backup_path.name, allow_missing=True)
            if backup_path.is_file():
                backup_stat = backup_path.stat()
                backup_digest = hashlib.sha256()
                with backup_path.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b''):
                        backup_digest.update(block)
                backup_after = backup_path.stat()
                verified = (backup_digest.hexdigest() == checksum and backup_stat.st_size == before.st_size
                            and (backup_stat.st_size, backup_stat.st_mtime_ns) == (backup_after.st_size, backup_after.st_mtime_ns))
        with self.store.guard():
            old = self.store.get('artifacts', artifact_id)
            same = old and old['sha256'] == checksum
            result = {'artifact_id': artifact_id, 'task_id': task_id, 'path': str(raw.resolve()), 'role': role,
                      'sha256': checksum, 'size': before.st_size, 'decision': decision if decision is not None else old.get('decision') if same else None,
                      'backup': str(backup_path) if backup_path else None, 'backup_verified': verified,
                      'backup_available': bool(backup_path and backup_path.is_file()),
                      'updated_at': now(), 'content_changed': bool(old and not same)}
            self.store.put('artifacts', artifact_id, result)
            self.store.event('artifact_observed', result)
            return result

    def experience(self, rule_id, code, operation, action, task_id=None, version='1', enabled=True):
        rule_id = _id(rule_id, 'Rule ID')
        if action not in ('verify_and_finalize', 'refresh_plan'):
            raise GovernanceError('UNSUPPORTED_EXPERIENCE_ACTION', 'Experience may only select a defined recovery action, never arbitrary code.')
        if task_id:
            self._task(task_id)
        if not isinstance(enabled, bool):
            raise GovernanceError('INVALID_EXPERIENCE', 'Experience enabled must be a boolean.')
        result = {'rule_id': rule_id, 'code': code, 'operation': operation, 'action': action,
                  'task_id': task_id, 'version': str(version), 'enabled': enabled, 'updated_at': now()}
        with self.store.guard():
            self.store.put('experience', rule_id, result)
            self.store.event('experience_registered', result)
        return result

    def match_experience(self, code, operation, task_id=None):
        matches = [r for r in self.store.list('experience') if r['enabled'] and r['version'] == '1'
                   and r['code'] == code and r['operation'] == operation and r['task_id'] in (None, task_id)]
        return {'matches': matches, 'code': code, 'operation': operation, 'task_id': task_id,
                'execution': 'A match is a candidate action; the executor must verify current evidence before applying it.'}
