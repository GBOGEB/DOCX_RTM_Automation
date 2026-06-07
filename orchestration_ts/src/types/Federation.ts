export interface FederationEvent {
  type: string;
  timestamp: string;
  payload: unknown;
}

export interface FederationStatus {
  federationId: string;
  state: string;
}
