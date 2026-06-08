import { app, config } from './server';

const port = Number(config.PORT);

app.listen(port, () => {
 console.log(`Orchestration server listening on ${port}`);
});
