#!/usr/bin/env python3
"""
Clash 订阅更新脚本
从机场拉取节点，合并到模板配置，生成最终订阅文件
"""

import os
import sys
import yaml
import requests
from datetime import datetime

# 订阅地址
SUB_URL = os.environ.get('SUB_URL', 'https://liangxin.xyz/api/v1/liangxin?OwO=4bfe667383e6019a0b004e78bb91d059')

# 文件路径
TEMPLATE_PATH = 'template.yaml'
OUTPUT_DIR = 'output'
OUTPUT_PATH = os.path.join(OUTPUT_DIR, 'clash_config.yaml')

def fetch_subscription(url: str) -> dict:
    """从机场拉取订阅配置"""
    headers = {
        'User-Agent': 'ClashMetaForAndroid/2.8.9'
    }
    
    try:
        print(f"📡 正在拉取订阅: {url[:50]}...")
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        config = yaml.safe_load(resp.text)
        print(f"✅ 订阅拉取成功，包含 {len(config.get('proxies', []))} 个节点")
        return config
    except Exception as e:
        print(f"❌ 拉取订阅失败: {e}")
        sys.exit(1)

def load_template() -> dict:
    """加载模板配置"""
    try:
        with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            template = yaml.safe_load(f)
        print(f"✅ 模板加载成功")
        return template
    except Exception as e:
        print(f"❌ 加载模板失败: {e}")
        sys.exit(1)

def categorize_proxies(proxies: list) -> dict:
    """将节点按地区分类"""
    categories = {
        'hk': [],      # 香港
        'jp': [],      # 日本
        'sg': [],      # 新加坡
        'us': [],      # 美国
        'uk': [],      # 英国
        'kr': [],      # 韩国
        'tw': [],      # 台湾
        'stream': [],  # 流媒体专线
        'other': []    # 其他
    }
    
    for proxy in proxies:
        name = proxy.get('name', '').upper()
        
        if '🇭🇰' in name or '香港' in name:
            categories['hk'].append(proxy)
        elif '🇯🇵' in name or '日本' in name:
            categories['jp'].append(proxy)
        elif '🇸🇬' in name or '新加坡' in name:
            categories['sg'].append(proxy)
        elif '🇺🇸' in name or '美国' in name:
            categories['us'].append(proxy)
        elif '🇬🇧' in name or '英国' in name:
            categories['uk'].append(proxy)
        elif '🇰🇷' in name or '韩国' in name:
            categories['kr'].append(proxy)
        elif '🇨🇳' in name or '台湾' in name:
            categories['tw'].append(proxy)
        elif '专线' in name or '流媒体' in name:
            categories['stream'].append(proxy)
        else:
            categories['other'].append(proxy)
    
    return categories

def build_proxy_groups(template_groups: list, proxies: list, categories: dict) -> list:
    """构建代理组"""
    all_proxy_names = [p['name'] for p in proxies]
    
    # 普通节点（排除流媒体专线）
    normal_proxies = [p for p in proxies if '专线' not in p.get('name', '') and '流媒体' not in p.get('name', '')]
    normal_names = [p['name'] for p in normal_proxies]
    
    # 流媒体专线
    stream_names = [p['name'] for p in categories['stream']]
    
    groups = []
    
    for group in template_groups:
        name = group['name']
        gtype = group['type']
        
        new_group = {
            'name': name,
            'type': gtype
        }
        
        # 添加 URL 测试配置
        if gtype in ['url-test', 'fallback']:
            new_group['url'] = group.get('url', 'http://www.gstatic.com/generate_204')
            new_group['interval'] = group.get('interval', 86400)
            if gtype == 'url-test':
                new_group['tolerance'] = group.get('tolerance', 100)
        
        # 根据组名填充节点
        if name == '良心云':
            new_group['proxies'] = ['自动选择', '故障转移'] + normal_names
        elif name == '自动选择':
            new_group['proxies'] = normal_names
        elif name == '故障转移':
            new_group['proxies'] = normal_names[:10]  # 只取前10个
        elif name == '流媒体':
            new_group['proxies'] = ['良心云'] + stream_names
        elif name == 'AI服务':
            # 美国/日本/英国优先
            ai_proxies = (categories['us'] + categories['jp'] + categories['uk'] + 
                         categories['sg'] + normal_names[:5])
            new_group['proxies'] = [p['name'] if isinstance(p, dict) else p for p in ai_proxies]
        elif name == 'Telegram':
            new_group['proxies'] = ['良心云'] + normal_names[:10]
        elif name in ['微软服务', '苹果服务']:
            new_group['proxies'] = ['DIRECT', '良心云'] + normal_names[:5]
        else:
            new_group['proxies'] = group.get('proxies', ['良心云'])
        
        groups.append(new_group)
    
    return groups

def merge_config(template: dict, subscription: dict) -> dict:
    """合并模板和订阅"""
    proxies = subscription.get('proxies', [])
    categories = categorize_proxies(proxies)
    
    # 构建新配置
    config = {
        'mixed-port': template.get('mixed-port', 7890),
        'allow-lan': template.get('allow-lan', False),
        'bind-address': template.get('bind-address', '*'),
        'mode': 'rule',
        'log-level': template.get('log-level', 'info'),
        'external-controller': template.get('external-controller', '127.0.0.1:9090'),
        'unified-delay': template.get('unified-delay', True),
        'tcp-concurrent': template.get('tcp-concurrent', True),
        'find-process-mode': template.get('find-process-mode', 'strict'),
        'global-client-fingerprint': template.get('global-client-fingerprint', 'safari'),
        'dns': template.get('dns', {}),
        'proxies': proxies,
        'proxy-groups': build_proxy_groups(
            template.get('proxy-groups', []),
            proxies,
            categories
        ),
        'rule-providers': template.get('rule-providers', {}),
        'rules': template.get('rules', [])
    }
    
    return config

def save_config(config: dict):
    """保存配置文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print(f"✅ 配置已保存到: {OUTPUT_PATH}")

def main():
    print("=" * 50)
    print("🚀 Clash 订阅更新脚本")
    print(f"⏰ 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 拉取订阅
    subscription = fetch_subscription(SUB_URL)
    
    # 加载模板
    template = load_template()
    
    # 合并配置
    print("🔀 正在合并配置...")
    config = merge_config(template, subscription)
    
    # 保存
    save_config(config)
    
    # 统计
    proxies_count = len(config.get('proxies', []))
    groups_count = len(config.get('proxy-groups', []))
    rules_count = len(config.get('rules', []))
    
    print("\n" + "=" * 50)
    print("📊 更新统计:")
    print(f"   - 节点数量: {proxies_count}")
    print(f"   - 代理组数: {groups_count}")
    print(f"   - 规则数量: {rules_count}")
    print("=" * 50)
    print("✅ 更新完成!")

if __name__ == '__main__':
    main()
