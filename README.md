# Clash Meta 自动订阅配置

自动从机场拉取节点，合并完整分流规则，定时更新。

## 订阅地址

```
https://raw.githubusercontent.com/Esingpawn/clash-sub-config/main/output/clash_config.yaml
```

## 使用方法

### FlClash (Windows)
1. 打开 FlClash → 配置 → 订阅
2. 添加订阅，粘贴上面的地址
3. 启用并更新

### Clash Meta (Android)
1. 打开 Clash Meta → 配置
2. 点击 "+" → 从 URL 导入
3. 粘贴上面的地址

## 自动更新

- GitHub Actions 每 6 小时自动更新一次
- 节点变化会自动同步
- 规则集每天自动更新

## 包含的规则

- ✅ 国内直连（百度、B站、淘宝等）
- ✅ Google/YouTube/GitHub 走代理
- ✅ Telegram 专用组
- ✅ AI 服务专用组（ChatGPT/Claude）
- ✅ 流媒体专用（Netflix 等）
- ✅ 广告拦截
- ✅ 微软/苹果服务可选直连

规则来源：blackmatrix7 (ios_rule_script)
