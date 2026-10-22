// E2E testy V2 (krok 11 docs/v2/05-plan.md). Backend beží s pamäťovým úložiskom (STORAGE=memory, AD-V2-09),
// takže testy nepotrebujú Supabase ani internet. Spustenie: npm run test:e2e
const path = require('node:path');
const { defineConfig, devices } = require('@playwright/test');

const PORT = 8001;  // iný port ako vývojový server (8000), aby sa nebili
// cmd.exe na Windows nepozná cestu s lomkami „/“, preto path.join.
const PYTHON = process.platform === 'win32'
  ? path.join('backend', '.venv', 'Scripts', 'python.exe')
  : path.join('backend', '.venv', 'bin', 'python');

module.exports = defineConfig({
  testDir: 'e2e',
  retries: 0,              // R-05 V1, R-P-04: každé zlyhanie je chyba, neopakuje sa
  workers: 1,              // spoločné pamäťové úložisko – testy uloženia sa nesmú prekrývať
  fullyParallel: false,
  timeout: 20_000,
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    trace: 'retain-on-failure',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `${PYTHON} -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port ${PORT}`,
    url: `http://127.0.0.1:${PORT}/api/health`,   // R-P-04: štart je hotový, až keď odpovedá API
    env: { STORAGE: 'memory' },
    reuseExistingServer: false,
    timeout: 30_000,
  },
});
