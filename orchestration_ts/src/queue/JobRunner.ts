import { JobQueue } from './JobQueue';

export class JobRunner {
 constructor(private readonly queue: JobQueue) {}

 runNext(): void {
  const job = this.queue.dequeue();
  if (!job) return;
  console.log(`Executing job ${job.id} (${job.type})`);
 }
}
