import { describe, expect, it } from 'vitest';
import { EventBus, FederationEvents } from '../src/events/EventBus';

describe('EventBus', () => {
  it('delivers a payload to every subscriber of the event', async () => {
    const bus = new EventBus();
    const seen: string[] = [];
    bus.subscribe(FederationEvents.PR_MERGED, p => { seen.push(`a:${p}`); });
    bus.subscribe(FederationEvents.PR_MERGED, async p => { seen.push(`b:${p}`); });
    await bus.publish(FederationEvents.PR_MERGED, 42);
    expect(seen.sort()).toEqual(['a:42', 'b:42']);
  });

  it('ignores events nobody subscribed to', async () => {
    const bus = new EventBus();
    let called = false;
    bus.subscribe(FederationEvents.PR_CREATED, () => { called = true; });
    await bus.publish(FederationEvents.SSOT_UPDATED, {});
    expect(called).toBe(false);
  });

  it('rejects when a handler throws', async () => {
    const bus = new EventBus();
    bus.subscribe('boom', () => { throw new Error('handler failed'); });
    await expect(bus.publish('boom', null)).rejects.toThrow('handler failed');
  });
});
