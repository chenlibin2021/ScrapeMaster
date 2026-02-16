#!/usr/bin/env python3
"""
获取免费代理列表并测试可用性 - 改进版
"""
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

def get_free_proxies():
    """从多个来源获取免费代理"""
    proxies = []
    
    # 来源1: GitHub geonode
    try:
        url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                ip = item.get('ip')
                port = item.get('port')
                if ip and port:
                    proxies.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"Geonode 获取失败: {e}")
    
    # 来源2: pubproxy
    try:
        url = "http://pubproxy.com/api/proxy?limit=20&format=json&type=http"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get('data', []):
                ip_port = item.get('ipPort')
                if ip_port:
                    proxies.append(f"http://{ip_port}")
    except Exception as e:
        print(f"Pubproxy 获取失败: {e}")
    
    # 来源3: 简单的HTML解析
    try:
        url = "https://www.sslproxies.org/"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            # 简单正则提取 IP:PORT
            matches = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td><td>(\d{2,5})</td>', response.text)
            for ip, port in matches[:30]:
                proxies.append(f"http://{ip}:{port}")
    except Exception as e:
        print(f"SSLProxies 获取失败: {e}")
    
    return list(set(proxies))[:100]  # 去重

def test_proxy(proxy, test_url="http://httpbin.org/ip", timeout=8):
    """测试代理是否可用"""
    try:
        proxies_dict = {
            "http": proxy,
            "https": proxy
        }
        response = requests.get(
            test_url,
            proxies=proxies_dict,
            timeout=timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        if response.status_code == 200:
            return {"proxy": proxy, "working": True, "response_time": response.elapsed.total_seconds()}
    except Exception:
        pass
    return {"proxy": proxy, "working": False}

def main():
    print("🔍 正在获取免费代理列表...")
    proxies = get_free_proxies()
    print(f"✅ 获取到 {len(proxies)} 个代理地址")
    
    if len(proxies) == 0:
        print("❌ 无法获取代理列表")
        return []
    
    print(f"\n🧪 正在测试代理可用性（测试前 {min(len(proxies), 50)} 个）...")
    working_proxies = []
    
    test_proxies = proxies[:50]  # 只测试前50个
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(test_proxy, proxy): proxy for proxy in test_proxies}
        
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            proxy_display = result['proxy'][:40] + "..." if len(result['proxy']) > 40 else result['proxy']
            print(f"[{i}/{len(test_proxies)}] {proxy_display:45} ", end="")
            if result['working']:
                print(f"✅ {result['response_time']:.2f}s")
                working_proxies.append(result)
            else:
                print("❌")
            
            # 找到3个可用的就可以了
            if len(working_proxies) >= 3:
                print("\n✅ 已找到足够的可用代理")
                executor.shutdown(wait=False, cancel_futures=True)
                break
    
    # 保存结果
    if working_proxies:
        working_proxies.sort(key=lambda x: x['response_time'])
        
        output_file = "/home/chenlibin/.openclaw/workspace/working_proxies.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(working_proxies, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 成功！找到 {len(working_proxies)} 个可用代理")
        print(f"📁 已保存到: {output_file}\n")
        print("可用代理列表:")
        for i, p in enumerate(working_proxies, 1):
            print(f"  {i}. {p['proxy']} ({p['response_time']:.2f}s)")
        
        return working_proxies
    else:
        print("\n❌ 未找到可用的代理")
        print("💡 建议：考虑使用付费代理服务或云服务器方案")
        return []

if __name__ == "__main__":
    main()
