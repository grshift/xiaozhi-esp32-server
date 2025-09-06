import { test, expect } from '@playwright/test';
import { execSync } from 'child_process';

// 定义一个类型来匹配 Python 脚本输出的 JSON 结构
interface SensorValues {
  temperature: number;
  humidity: number;
  battery_level: number;
  signal_strength: number;
}

// 声明一个变量来存储从 Python 脚本中解析出的传感器值
let testValues: SensorValues;
const testDeviceId = "sensor-e2e-test-01";

test.beforeAll(() => {
  // 执行 Python 脚本并捕获其标准输出
  const output = execSync('python3 utils/mock_sensor_data.py').toString();
  
  // 从输出中用正则表达式解析出我们发送的 JSON 格式的测试值
  const match = output.match(/E2E_TEST_VALUES=({.*})/);
  if (!match || !match[1]) {
    throw new Error("Could not parse E2E_TEST_VALUES from mock sensor script output.");
  }
  
  // 将解析出的字符串转换为 JSON 对象
  testValues = JSON.parse(match[1]);
  console.log(`Test will run with sensor values:`, testValues);
});

test('should select a device and display its latest sensor data in the table', async ({ page }) => {
  // 1. 导航到传感器管理页面
  // ❗ 重要: 根据你的截图，端口似乎是 59565。如果这个端口是动态的，请在运行前确认。
  await page.goto('http://localhost:59565/#/sensor-management');

  // 2. 选择我们的测试设备
  // ❗ 重要: 下面的选择器是基于截图的猜测，你很可能需要根据你的 HTML 结构进行调整。
  //    我们首先点击下拉框来展开选项。
  const deviceSelectorDropdown = page.locator('input[placeholder="选择设备"]');
  await deviceSelectorDropdown.click();

  //    然后在弹出的选项中，点击与我们测试设备ID匹配的选项。
  await page.locator(`li:has-text("${testDeviceId}")`).click();
  
  // 3. 验证表格中显示的传感器数据
  //    我们将通过查找包含传感器名称的行，然后定位到该行的“最新值”单元格来进行验证。
  // ❗ 提示: 如果你的表格是用 <div> 而不是 <table> 实现的，你可能需要将 'tr'/'td' 替换掉。
  
  // 定义“最新值”列的索引 (从0开始计数)。根据截图: 传感器编码(0), 名称(1), 类型(2), 间隔(3), 最新值(4)
  const latestValueColumnIndex = 4;

  // 验证温度
  // ❗ 提示: 如果你的表格中显示的传感器名称是中文 (例如 "温度"), 
  //    请将下面的 'temperature' 修改为 '温度'。
  const tempRow = page.locator(`tr:has-text("temperature")`);
  await expect(tempRow.locator('td').nth(latestValueColumnIndex)).toHaveText(String(testValues.temperature));

  // 验证湿度
  const humidityRow = page.locator(`tr:has-text("humidity")`);
  await expect(humidityRow.locator('td').nth(latestValueColumnIndex)).toHaveText(String(testValues.humidity));

  // 验证电池电量
  const batteryRow = page.locator(`tr:has-text("battery_level")`);
  await expect(batteryRow.locator('td').nth(latestValueColumnIndex)).toHaveText(String(testValues.battery_level)); 

  // 验证信号强度
  const signalRow = page.locator(`tr:has-text("signal_strength")`);
  await expect(signalRow.locator('td').nth(latestValueColumnIndex)).toHaveText(String(testValues.signal_strength));

  // （可选）截图以供调试
  await page.screenshot({ path: 'e2e-tests/screenshots/sensor-management-table.png' });
});
