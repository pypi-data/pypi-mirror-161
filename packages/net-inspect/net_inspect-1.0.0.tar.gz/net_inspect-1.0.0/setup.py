# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['net_inspect', 'net_inspect.plugins']

package_data = \
{'': ['*']}

install_requires = \
['ntc_templates_elinpf>=3.2.0,<4.0.0',
 'python-Levenshtein-wheels>=0.13.2,<0.14.0',
 'rich>=12.4.1,<13.0.0',
 'rich_typer>=0.1.5,<0.2.0',
 'textfsm>=1.1.2,<2.0.0']

entry_points = \
{'console_scripts': ['net_inspect = net_inspect.cli:app']}

setup_kwargs = {
    'name': 'net-inspect',
    'version': '1.0.0',
    'description': '基于已收集的网络设备信息进行的结构化数据分析框架',
    'long_description': '# net_inspect 介绍\n\n`net_inspect`是网络设备数据结构化分析框架\n\n\n## 安装方法\n\n### PyPI\n\n```bash\npip install net_inspect\n```\n\n### Poetry\n\n```bash\ngit clone https://github.com/Elinpf/net_inspect\ncd net_inspect\npoetry install\n```\n\n## 插件介绍\n\n`net_inspect`采用了插件模块的框架，分别是`Input`, `Parse`, `Analysis`, `Output` 模块。\n\n通过编写模块插件，实现快速定制的能力。\n\n### InputPlugin\n\nInput插件的功能是将**已经获得的设备检查命令的日志**转化为命令与命令输出的对应关系。如果是通过直接对设备进行操作获取的日志，可以使用`console`这个插件进行处理。如果是用的第三方平台进行的自动化收集，那么就需要自行编写Input插件实现命令与输出的对应。\n\n### ParsePlugin\n\nParse插件的功能是将每条命令的输出进行解析并且结构化。提取出关键信息并以`List[dict]`的方式进行存储。\n\n现有的`Parse`解析模块使用的是[ntc-templates-elinpf](https://github.com/Elinpf/ntc-templates)这个库，是`ntc-templates`库的分支，由于主仓更新频率很慢且不会增加国内常用的设备厂家，所以我Fork后进行了修改。\n\n\n### AnalysisPlugin\n\nAnalysis插件的功能是将解析的信息进行分析，对分析的内容进行告警分级。例如电源是否异常。这个工作是在分析模块中进行的。\n\n### OutputPlugin\n\n输出模块可能是最需要自定义编写的地方。将解析和分析的结果按照自己想要的格式展现出来。\n\n## 使用方法\n\n`net_inspect`有三种使用方式\n\n1. 作为三方库提供API\n2. CLI命令行操作\n3. 本地Web界面操作 (TODO)\n\n\n### 使用库\n\n示例:\n\n```python\nfrom net_inspect import NetInspect, OutputPluginAbstract, PluginError\nfrom rich.table import Table\nfrom rich.console import Console\n\n\nclass Output(OutputPluginAbstract):\n    def main(self):\n        if not self.args.output_params.get(\'company\'):\n            raise PluginError(\'name or age is missing\')\n\n        console = Console()\n\n        table = Table(title=self.args.output_params.get(\n            \'company\'), show_lines=False)\n        table.add_column(\'name\', justify=\'center\')\n        table.add_column(\'ip\', justify=\'center\')\n        table.add_column(\'model\', justify=\'center\')\n        table.add_column(\'version\', justify=\'center\')\n        table.add_column(\'power\', justify=\'center\')\n\n        for device in self.args.devices:\n            if device.vendor.PLATFORM == \'huawei_vrp\':\n                data = [device.info.name, device.info.ip]\n                ps = device.parse_result(\'display version\')\n                data.append(ps[0].get(\'model\'))\n                data.append(ps[0].get(\'vrp_version\'))\n                power_analysis = device.analysis_result.get(\'Power Status\')\n                power_desc = []\n                for alarm in power_analysis:\n                    if alarm.include_focus:\n                        power_desc.append(alarm.message)\n                data.append(\'\\n\'.join(power_desc) if power_desc else \'Normal\')\n\n                table.add_row(*data)\n                table.row_styles = [\'green\']\n\n        console.print(table)\n\n\nnet = NetInspect()\n# net.set_log_level(\'DEBUG\')\nnet.set_plugins(\'smartone\', Output)\ncluster = net.run(\'log_files\', output_plugin_params={\'company\': \'Company Name\'})\n```\n\n## API 解释\n\n### 初始化\n\n```python\nfrom net_inspect import NetInspect\n\nnet = NetInspect()\n```\n\n### 设置日志级别\n\n```python\nnet.verbose(1)\n```\n\n开启`verbose`表示为打开了`DEBUG`级别的日志, 默认为`INFO`。\n`verbose`级别可以通过`verbose()`方法设置，总共0~3\n- 0: 日志关闭\n- 1: 提供Output模块的日志和Parse模块的日志\n- 2: 追加提供Analysis模块的日志\n- 3: 追加提供Parse模块不支持命令的信息日志和命令为无效的信息\n\n### 设置插件\n\n一般来说，只需要设置`input_plugin`和`output_plugin`即可。\n\n```python\nnet.set_plugins(input_plugin=\'smartone\', output_plugin=\'device_warning_logging\')\n```\n可以使用字符串的简写，也可以自己继承插件类后重写`main()`方法，然后将类传递进来。\n\n### 执行\n\n提供输入的文件路径即可, 可以是文件或者目录。\n\n```python\nnet.run(\'log_files\')\n```\n\n如果output中需要提供参数，可以使用`output_plugin_params`参数，例如：\n\n```python\nnet.run(\'log_files\', output_plugin_params={\'company\': \'Company Name\'})\n```\n\n## CLI 命令行操作\n\n![](resource/cli_1.png)\n\n```bash\nnet_inspect -i log_files\n```\n\n\n\n## 关于贡献\n\n分析插件还在持续开发中，`develop_script.py`脚本就是为高效开发提供的一个工具。\n\n开发一个分析插件的流程，以开发检查风扇状态的`fan_status`插件为例：\n\n1. 创建一个新的插件文件, 对应的文件初始状态会一并准备好\n\n```bash\npython ./develop_script.py -p fan_status -g\n```\n\n2. 在对应的文件中实现插件对每个厂商分析的函数\n\n```py\nclass AnalysisPluginWithFanStatus(AnalysisPluginAbc):\n    """\n    要求设备所有在位风扇模块运行在正常状态。\n    """\n    @analysis.vendor(vendor.H3C)\n    @analysis.template_key(\'hp_comware_display_fan.textfsm\', [\'slot\', \'id\', \'status\'])\n    def hp_comware(template: TemplateInfo, result: AnalysisResult):\n        """模块状态不为Normal的时候告警"""\n        for row in template[\'display fan\']:\n            if row[\'status\'].lower() != \'normal\':\n                result.add_warning(\n                    f\'Slot {row["slot"]} Fan {row["id"]} 状态异常\' if row[\'slot\'] else f\'Fan {row["id"]} 状态异常\')\n```\n\n其中`@analysis`是用来记录插件的分析类型的，`vendor`记录插件的厂商类型，`template_key`记录分析模块所需要的`textfsm`文件以及里面的哪些值。\n这些值会在参数`template: TemplateInfo`中给出。\n\n`result: AnalysisResult`用来记录分析结果。可以添加告警信息。\n\n分析方法为类方法，不需要`self`,不需要给出返回值。\n\n插件中的类注释和方法注释都会被记录下来，方便后续调用。\n\n3. 创建对应的测试文件\n\n当编写了对应的分析方法后，再次执行创建命令，工具会自动根据分析方法中需要的命令，生成对应的测试文件。\n\n测试文件路径为`tests/check_analysis_plugins/<plugin_name>/<funcation_name>.raw`\n\n```bash\npython ./development_script.py -p fan_status -f hp_comware -g\n```\n\n4. 在测试文件中添加测试用例\n5. 执行测试\n\n```bash\npython ./development_script.py -p fan_status -f hp_comware -t\n```\n\n6. 完成测试，确认测试结果为正常后，生成yml文件作为参考文件。\n\n```bash\npython ./development_script.py -p fan_status -f hp_comware -y\n```\n\n',
    'author': 'Elin',
    'author_email': '365433079@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Elinpf/net_inspect',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
