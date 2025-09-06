import { chromium, FullConfig } from '@playwright/test';

// 定义一个常量来存储登录状态文件的路径
const authFile = 'playwright/.auth/user.json';

async function globalSetup(config: FullConfig) {
  // 手动启动一个浏览器实例
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    // 1. 导航到登录页面
    // ❗ 重要: 如果 59565 端口不正确或经常变化，请在这里修改为正确的端口
    await page.goto('http://localhost:59565/#/login');

    // 2. 输入用户名和密码，然后点击登录按钮
    // ❗ 重要: 
    //    - 将 'your_username' 和 'your_password' 替换为真实的测试账号和密码。
    //    - 使用开发者工具（F12）检查并确认下面的选择器是正确的。
    await page.locator('input[placeholder*="账号"]').fill('your_username');
    await page.locator('input[placeholder*="密码"]').fill('your_password');
    await page.locator('button:has-text("登录")').click(); // 假设按钮文本是 "登录"

    // 3. 等待并验证登录成功
    //    等待页面跳转到登录后的某个特定 URL，这是确保我们真的登录成功了的关键一步。
    await page.waitForURL(/.*sensor-management/, { timeout: 10000 });

    // 4. 保存登录状态到我们之前定义的文件中
    await page.context().storageState({ path: authFile });
    console.log('✅ 登录状态已成功保存!');

  } catch (error) {
    console.error('❌ 全局登录设置失败:', error);
    // 在 CI 环境中，如果登录失败，我们可能希望整个测试都失败
    process.exit(1);
  } finally {
    // 确保浏览器被关闭
    await browser.close();
  }
}

export default globalSetup;
