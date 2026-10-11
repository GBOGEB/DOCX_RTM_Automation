import request from 'supertest';
import { describe, expect, it } from 'vitest';
import { app, config } from '../src/server';
import { ConfigSchema } from '../src/config/config';

describe('server', () => {
  it('reports health with the federation id', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body).toEqual({ status: 'ok', federation: config.FEDERATION_ID });
  });

  it('reports bootstrap federation status', async () => {
    const res = await request(app).get('/federation/status');
    expect(res.body.state).toBe('bootstrap');
  });
});

describe('config', () => {
  it('fills defaults for missing environment values', () => {
    expect(ConfigSchema.parse({})).toEqual({
      PORT: '3000',
      NODE_ENV: 'development',
      LOG_LEVEL: 'info',
      FEDERATION_ID: 'DOCX_RTM_AUTOMATION',
    });
  });
});
