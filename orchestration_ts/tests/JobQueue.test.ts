import { describe, expect, it, vi } from 'vitest';
import { JobQueue } from '../src/queue/JobQueue';
import { JobRunner } from '../src/queue/JobRunner';

describe('JobQueue', () => {
  it('dequeues jobs in FIFO order and tracks size', () => {
    const queue = new JobQueue();
    queue.enqueue({ id: '1', type: 'parse', payload: null });
    queue.enqueue({ id: '2', type: 'patch', payload: null });
    expect(queue.size()).toBe(2);
    expect(queue.dequeue()?.id).toBe('1');
    expect(queue.dequeue()?.id).toBe('2');
    expect(queue.dequeue()).toBeUndefined();
    expect(queue.size()).toBe(0);
  });
});

describe('JobRunner', () => {
  it('runs the next job and is a no-op on an empty queue', () => {
    const queue = new JobQueue();
    const runner = new JobRunner(queue);
    const log = vi.spyOn(console, 'log').mockImplementation(() => {});
    runner.runNext();
    expect(log).not.toHaveBeenCalled();
    queue.enqueue({ id: '7', type: 'validate', payload: {} });
    runner.runNext();
    expect(log).toHaveBeenCalledWith('Executing job 7 (validate)');
    expect(queue.size()).toBe(0);
    log.mockRestore();
  });
});
