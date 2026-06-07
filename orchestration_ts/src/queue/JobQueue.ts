export interface Job<T = unknown> {
 id: string;
 type: string;
 payload: T;
}

export class JobQueue {
 private readonly jobs: Job[] = [];

 enqueue(job: Job): void {
  this.jobs.push(job);
 }

 dequeue(): Job | undefined {
  return this.jobs.shift();
 }

 size(): number {
  return this.jobs.length;
 }
}
