# Skill Creator V2

Skill Creator V2 是一个用于创建 AI skills 和 skill groups 的元技能，重点是生产级流程和证据。

当你需要的不只是一个看起来完成的 prompt，而是有文档、可测试、声明依赖、记录失败模式并保留验证证据的 skill 时，它会很有用。

使用方式：安装 npm 包，把 skill 安装到目标 runtime，然后让 agent 创建或改进某个 skill。它会分类请求，只加载必要的参考文件，验证工具和依赖，在适用时运行 lint/evals，并生成 readiness report。

预期结果：一个结构化包，包括 `SKILL.md`、references、scripts、evals、tests，以及基于证据的 review。

示例：UI Intelligence group 从浅层参考收集升级为 live-site evidence、滚动截图、公开代码/字体/效果 metadata、原创性检查，以及把实际失败反馈回 skill 的改进循环。
