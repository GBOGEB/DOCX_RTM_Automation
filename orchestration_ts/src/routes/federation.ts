export interface FederationEventRequest {
 type: string;
 payload: unknown;
}

export function handleFederationEvent(event: FederationEventRequest) {
 return {
  accepted: true,
  eventType: event.type,
  receivedAt: new Date().toISOString()
 };
}
