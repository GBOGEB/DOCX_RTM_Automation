
/**
 * TypeScript Orchestration Server
 * CMB-ready enterprise integration with API endpoints and webhook handlers
 */

import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import winston from 'winston';
import { body, validationResult } from 'express-validator';
import multer from 'multer';
import path from 'path';
import fs from 'fs/promises';
import { spawn } from 'child_process';
import cron from 'node-cron';

// Types and Interfaces
interface DocumentProcessingRequest {
  documentPath: string;
  processingOptions: {
    extractRTM: boolean;
    extractOTC: boolean;
    extractDEL: boolean;
    generateVisualizations: boolean;
    runDMAIC: boolean;
  };
  metadata: {
    projectName: string;
    requestedBy: string;
    priority: 'low' | 'medium' | 'high';
  };
}

interface ProcessingResult {
  jobId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  results?: any;
  error?: string;
  startTime: Date;
  endTime?: Date;
}

interface WebhookPayload {
  event: string;
  data: any;
  timestamp: Date;
  source: string;
}

interface DMAICIteration {
  iterationId: string;
  phase: 'define' | 'measure' | 'analyze' | 'improve' | 'control';
  status: string;
  complianceScore: number;
  deliverables: string[];
}

// Logger configuration
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'orchestration-server' },
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// Express app setup
const app = express();
const server = createServer(app);
const io = new SocketIOServer(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.'
});
app.use('/api/', limiter);

// File upload configuration
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = 'uploads';
    try {
      await fs.mkdir(uploadDir, { recursive: true });
      cb(null, uploadDir);
    } catch (error) {
      cb(error, uploadDir);
    }
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: {
    fileSize: 100 * 1024 * 1024 // 100MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.docx', '.doc', '.pdf', '.txt'];
    const ext = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(ext)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only DOCX, DOC, PDF, and TXT files are allowed.'));
    }
  }
});

// In-memory job storage (in production, use Redis or database)
const processingJobs = new Map<string, ProcessingResult>();
const dmaicIterations = new Map<string, DMAICIteration>();

// Utility functions
function generateJobId(): string {
  return `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function generateIterationId(): string {
  return `dmaic_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

async function executeDocumentProcessing(jobId: string, request: DocumentProcessingRequest): Promise<void> {
  const job = processingJobs.get(jobId);
  if (!job) return;

  try {
    job.status = 'processing';
    job.progress = 10;
    
    // Emit progress update
    io.emit('job-progress', { jobId, progress: job.progress, status: job.status });

    // Execute Python document processor
    const pythonProcess = spawn('python3', [
      '/home/ubuntu/workspace/master_doc_processor.py',
      '--input', request.documentPath,
      '--output', `processing_results/${jobId}`
    ]);

    job.progress = 30;
    io.emit('job-progress', { jobId, progress: job.progress, status: job.status });

    pythonProcess.on('close', async (code) => {
      if (code === 0) {
        job.progress = 60;
        io.emit('job-progress', { jobId, progress: job.progress, status: job.status });

        // Execute visualization system if requested
        if (request.processingOptions.generateVisualizations) {
          const vizProcess = spawn('python3', [
            '/home/ubuntu/workspace/enhanced_visualization_system.py',
            '--input', `processing_results/${jobId}/analysis.json`,
            '--output', `processing_results/${jobId}/visualizations`
          ]);

          vizProcess.on('close', (vizCode) => {
            job.progress = 80;
            io.emit('job-progress', { jobId, progress: job.progress, status: job.status });

            if (vizCode === 0) {
              job.status = 'completed';
              job.progress = 100;
              job.endTime = new Date();
              job.results = {
                analysisPath: `processing_results/${jobId}/analysis.json`,
                visualizationsPath: `processing_results/${jobId}/visualizations`,
                message: 'Document processing completed successfully'
              };
            } else {
              job.status = 'failed';
              job.error = 'Visualization generation failed';
            }
            
            io.emit('job-complete', { jobId, status: job.status, results: job.results, error: job.error });
          });
        } else {
          job.status = 'completed';
          job.progress = 100;
          job.endTime = new Date();
          job.results = {
            analysisPath: `processing_results/${jobId}/analysis.json`,
            message: 'Document processing completed successfully'
          };
          io.emit('job-complete', { jobId, status: job.status, results: job.results });
        }
      } else {
        job.status = 'failed';
        job.error = 'Document processing failed';
        io.emit('job-complete', { jobId, status: job.status, error: job.error });
      }
    });

  } catch (error) {
    job.status = 'failed';
    job.error = error instanceof Error ? error.message : 'Unknown error occurred';
    io.emit('job-complete', { jobId, status: job.status, error: job.error });
  }
}

// API Routes

// Health check endpoint
app.get('/api/health', (req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '2.0.0',
    services: {
      documentProcessor: 'available',
      visualizationEngine: 'available',
      dmaicPipeline: 'available'
    }
  });
});

// Document upload and processing endpoint
app.post('/api/documents/process', 
  upload.single('document'),
  [
    body('processingOptions.extractRTM').isBoolean(),
    body('processingOptions.extractOTC').isBoolean(),
    body('processingOptions.extractDEL').isBoolean(),
    body('processingOptions.generateVisualizations').isBoolean(),
    body('processingOptions.runDMAIC').isBoolean(),
    body('metadata.projectName').isString().isLength({ min: 1 }),
    body('metadata.requestedBy').isString().isLength({ min: 1 }),
    body('metadata.priority').isIn(['low', 'medium', 'high'])
  ],
  async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      if (!req.file) {
        return res.status(400).json({ error: 'No document file uploaded' });
      }

      const jobId = generateJobId();
      const processingRequest: DocumentProcessingRequest = {
        documentPath: req.file.path,
        processingOptions: req.body.processingOptions,
        metadata: req.body.metadata
      };

      const job: ProcessingResult = {
        jobId,
        status: 'pending',
        progress: 0,
        startTime: new Date()
      };

      processingJobs.set(jobId, job);

      // Start processing asynchronously
      executeDocumentProcessing(jobId, processingRequest);

      logger.info(`Document processing job started: ${jobId}`, { 
        filename: req.file.originalname,
        projectName: processingRequest.metadata.projectName 
      });

      res.json({
        jobId,
        status: 'pending',
        message: 'Document processing started',
        estimatedDuration: '5-10 minutes'
      });

    } catch (error) {
      logger.error('Error starting document processing', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

// Job status endpoint
app.get('/api/jobs/:jobId', (req: Request, res: Response) => {
  const { jobId } = req.params;
  const job = processingJobs.get(jobId);

  if (!job) {
    return res.status(404).json({ error: 'Job not found' });
  }

  res.json(job);
});

// List all jobs endpoint
app.get('/api/jobs', (req: Request, res: Response) => {
  const jobs = Array.from(processingJobs.values());
  res.json({
    jobs,
    total: jobs.length,
    active: jobs.filter(j => j.status === 'processing').length,
    completed: jobs.filter(j => j.status === 'completed').length,
    failed: jobs.filter(j => j.status === 'failed').length
  });
});

// DMAIC iteration endpoints
app.post('/api/dmaic/iterations',
  [
    body('projectName').isString().isLength({ min: 1 }),
    body('objectives').isArray().isLength({ min: 1 }),
    body('phase').isIn(['define', 'measure', 'analyze', 'improve', 'control'])
  ],
  async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({ errors: errors.array() });
      }

      const iterationId = generateIterationId();
      const iteration: DMAICIteration = {
        iterationId,
        phase: req.body.phase,
        status: 'active',
        complianceScore: 0,
        deliverables: []
      };

      dmaicIterations.set(iterationId, iteration);

      logger.info(`DMAIC iteration created: ${iterationId}`, { 
        projectName: req.body.projectName,
        phase: req.body.phase 
      });

      res.json({
        iterationId,
        status: 'created',
        message: 'DMAIC iteration initialized successfully'
      });

    } catch (error) {
      logger.error('Error creating DMAIC iteration', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  }
);

app.get('/api/dmaic/iterations/:iterationId', (req: Request, res: Response) => {
  const { iterationId } = req.params;
  const iteration = dmaicIterations.get(iterationId);

  if (!iteration) {
    return res.status(404).json({ error: 'DMAIC iteration not found' });
  }

  res.json(iteration);
});

app.get('/api/dmaic/iterations', (req: Request, res: Response) => {
  const iterations = Array.from(dmaicIterations.values());
  res.json({
    iterations,
    total: iterations.length,
    byPhase: {
      define: iterations.filter(i => i.phase === 'define').length,
      measure: iterations.filter(i => i.phase === 'measure').length,
      analyze: iterations.filter(i => i.phase === 'analyze').length,
      improve: iterations.filter(i => i.phase === 'improve').length,
      control: iterations.filter(i => i.phase === 'control').length
    }
  });
});

// Webhook endpoint for external integrations
app.post('/api/webhooks/:source', async (req: Request, res: Response) => {
  try {
    const { source } = req.params;
    const payload: WebhookPayload = {
      event: req.body.event || 'unknown',
      data: req.body.data || req.body,
      timestamp: new Date(),
      source
    };

    logger.info(`Webhook received from ${source}`, { event: payload.event });

    // Process webhook based on source and event
    await processWebhook(payload);

    // Emit webhook event to connected clients
    io.emit('webhook-received', payload);

    res.json({ status: 'received', timestamp: payload.timestamp });

  } catch (error) {
    logger.error('Error processing webhook', error);
    res.status(500).json({ error: 'Webhook processing failed' });
  }
});

async function processWebhook(payload: WebhookPayload): Promise<void> {
  switch (payload.source) {
    case 'github':
      await processGitHubWebhook(payload);
      break;
    case 'jira':
      await processJiraWebhook(payload);
      break;
    case 'confluence':
      await processConfluenceWebhook(payload);
      break;
    default:
      logger.warn(`Unknown webhook source: ${payload.source}`);
  }
}

async function processGitHubWebhook(payload: WebhookPayload): Promise<void> {
  if (payload.event === 'push') {
    // Trigger document reprocessing if relevant files changed
    logger.info('GitHub push event received, checking for document updates');
  } else if (payload.event === 'pull_request') {
    // Handle PR events for automated reviews
    logger.info('GitHub PR event received');
  }
}

async function processJiraWebhook(payload: WebhookPayload): Promise<void> {
  if (payload.event === 'issue_updated') {
    // Update DMAIC iteration based on Jira issue changes
    logger.info('Jira issue update received');
  }
}

async function processConfluenceWebhook(payload: WebhookPayload): Promise<void> {
  if (payload.event === 'page_updated') {
    // Trigger document synchronization
    logger.info('Confluence page update received');
  }
}

// Analytics and reporting endpoints
app.get('/api/analytics/dashboard', async (req: Request, res: Response) => {
  try {
    const jobs = Array.from(processingJobs.values());
    const iterations = Array.from(dmaicIterations.values());

    const analytics = {
      processing: {
        totalJobs: jobs.length,
        successRate: jobs.length > 0 ? jobs.filter(j => j.status === 'completed').length / jobs.length : 0,
        averageProcessingTime: calculateAverageProcessingTime(jobs),
        jobsByStatus: {
          pending: jobs.filter(j => j.status === 'pending').length,
          processing: jobs.filter(j => j.status === 'processing').length,
          completed: jobs.filter(j => j.status === 'completed').length,
          failed: jobs.filter(j => j.status === 'failed').length
        }
      },
      dmaic: {
        totalIterations: iterations.length,
        averageComplianceScore: iterations.length > 0 ? 
          iterations.reduce((sum, i) => sum + i.complianceScore, 0) / iterations.length : 0,
        iterationsByPhase: {
          define: iterations.filter(i => i.phase === 'define').length,
          measure: iterations.filter(i => i.phase === 'measure').length,
          analyze: iterations.filter(i => i.phase === 'analyze').length,
          improve: iterations.filter(i => i.phase === 'improve').length,
          control: iterations.filter(i => i.phase === 'control').length
        }
      },
      system: {
        uptime: process.uptime(),
        memoryUsage: process.memoryUsage(),
        timestamp: new Date().toISOString()
      }
    };

    res.json(analytics);

  } catch (error) {
    logger.error('Error generating analytics', error);
    res.status(500).json({ error: 'Analytics generation failed' });
  }
});

function calculateAverageProcessingTime(jobs: ProcessingResult[]): number {
  const completedJobs = jobs.filter(j => j.status === 'completed' && j.endTime);
  if (completedJobs.length === 0) return 0;

  const totalTime = completedJobs.reduce((sum, job) => {
    return sum + (job.endTime!.getTime() - job.startTime.getTime());
  }, 0);

  return totalTime / completedJobs.length / 1000; // Return in seconds
}

// WebSocket connection handling
io.on('connection', (socket) => {
  logger.info(`Client connected: ${socket.id}`);

  socket.on('subscribe-job', (jobId: string) => {
    socket.join(`job-${jobId}`);
    logger.info(`Client ${socket.id} subscribed to job ${jobId}`);
  });

  socket.on('subscribe-dmaic', (iterationId: string) => {
    socket.join(`dmaic-${iterationId}`);
    logger.info(`Client ${socket.id} subscribed to DMAIC iteration ${iterationId}`);
  });

  socket.on('disconnect', () => {
    logger.info(`Client disconnected: ${socket.id}`);
  });
});

// Scheduled tasks
cron.schedule('0 */6 * * *', async () => {
  // Clean up old completed jobs every 6 hours
  const cutoffTime = new Date(Date.now() - 24 * 60 * 60 * 1000); // 24 hours ago
  
  for (const [jobId, job] of processingJobs.entries()) {
    if (job.status === 'completed' && job.endTime && job.endTime < cutoffTime) {
      processingJobs.delete(jobId);
      logger.info(`Cleaned up old job: ${jobId}`);
    }
  }
});

// Error handling middleware
app.use((error: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error('Unhandled error', error);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// Server startup
const PORT = process.env.PORT || 3000;

server.listen(PORT, () => {
  logger.info(`Orchestration server started on port ${PORT}`);
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
  console.log(`📡 WebSocket endpoint: ws://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

export default app;
