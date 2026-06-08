export type EventHandler<T = unknown> = (payload: T) => Promise<void> | void;

export class EventBus {
  private handlers = new Map<string, EventHandler[]>();

  subscribe(event: string, handler: EventHandler): void {
    const existing = this.handlers.get(event) ?? [];
    existing.push(handler);
    this.handlers.set(event, existing);
  }

  async publish<T>(event: string, payload: T): Promise<void> {
    const handlers = this.handlers.get(event) ?? [];
    await Promise.all(handlers.map(h => Promise.resolve(h(payload))));
  }
}

export const FederationEvents = {
  SSOT_UPDATED: 'SSOT_UPDATED',
  PARSE_COMPLETE: 'PARSE_COMPLETE',
  PATCH_COMMITTED: 'PATCH_COMMITTED',
  PR_CREATED: 'PR_CREATED',
  PR_MERGED: 'PR_MERGED',
  AGENT_DISPATCH: 'AGENT_DISPATCH',
  AGENT_RESULT: 'AGENT_RESULT',
  VALIDATION_FAILED: 'VALIDATION_FAILED',
  HANDOVER_READY: 'HANDOVER_READY'
} as const;
