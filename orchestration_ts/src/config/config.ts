import { z } from 'zod';

export const ConfigSchema = z.object({
 PORT: z.string().default('3000'),
 NODE_ENV: z.string().default('development'),
 LOG_LEVEL: z.string().default('info'),
 FEDERATION_ID: z.string().default('DOCX_RTM_AUTOMATION')
});

export type AppConfig = z.infer<typeof ConfigSchema>;

export function loadConfig(): AppConfig {
 return ConfigSchema.parse(process.env);
}
