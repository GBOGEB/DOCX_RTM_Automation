import express from 'express';
import { loadConfig } from './config/config';

const app = express();
const config = loadConfig();

app.get('/health', (_req, res) => {
 res.json({ status: 'ok', federation: config.FEDERATION_ID });
});

app.get('/federation/status', (_req, res) => {
 res.json({ federation: config.FEDERATION_ID, state: 'bootstrap' });
});

export { app, config };
