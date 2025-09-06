import { defineConfig } from '@playwright/test';

export default defineConfig({
  // 测试文件的存放目录
  testDir: './tests',
  
  // 测试超时时间，设置为 30 秒
  timeout: 30 * 1000,
  
  // 断言的默认超时时间
  expect: {
    timeout: 5000
  },
  
  // 禁止并行测试，对于简单的端到端测试原型来说更稳定
  workers: 1,

  // 测试报告器
  reporter: 'html',

  /* 全局设置: 在所有测试运行之前执行的设置 */
  globalSetup: require.resolve('./tests/auth.setup.ts'),

  use: {
    // 无头模式运行浏览器。在 CI 环境中应为 true, 本地调试时可以设为 false
    headless: true,

    // 忽略 HTTPS 错误
    ignoreHTTPSErrors: true,
    
    // 截图策略：仅在失败时截图
    screenshot: 'only-on-failure',

    // 视频录制策略：仅在第一次重试时录制
    video: 'on-first-retry',
    
    // 追踪每个测试的执行过程，生成 trace.zip 文件
    trace: 'on', // 在调试时可以设置为 'on'
    
    // 复用登录状态
    // 所有测试都将使用这个文件中的状态，从而跳过登录步骤
    storageState: 'playwright/.auth/user.json',
  },
});
