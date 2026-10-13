# ADC_DEMO

TM4C1294NCPDT 双通道 ADC 采样示例，使用 Keil μVision 工程 `adc_demo.uvprojx` 构建。

| 目录 | 内容 |
| --- | --- |
| `app/` | ADC 示例入口与采样、定时逻辑 |
| `bsp/` | TM1638 显示与按键驱动 |
| `driverlib/`、`inc/` | TI 驱动库与芯片寄存器头文件 |
| `RTE/` | Keil 管理的启动与系统文件 |
| `tools/` | 编码转换脚本 |
| `Objects/`、`Listings/` | Keil 构建输出 |

在项目根目录打开 `adc_demo.uvprojx` 并构建 `Target 1`。

需要将工程代码文本转为 UTF-8 时，在项目根目录运行：

```powershell
python tools/convert_project_to_utf8.py
```

脚本递归扫描项目根目录，按脚本内的扩展名列表处理代码及工程文本文件；跳过构建输出目录和 `backup/`。转换前会在项目根目录的 `backup/` 下按原相对路径创建 `.bak` 备份。
