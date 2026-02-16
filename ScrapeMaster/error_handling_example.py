# 错误处理示例 - 添加到现有函数中

import logging
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scrapemaster.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def safe_scrape_with_retry(url, max_retries=3):
    """带重试的安全爬取函数"""
    for attempt in range(max_retries):
        try:
            logger.info(f"尝试爬取 {url} (第{attempt+1}次)")
            # 这里替换为实际的爬取逻辑
            # result = scrape_function(url)
            return "爬取结果"
            
        except TimeoutError:
            logger.warning(f"请求超时，{attempt+1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error(f"爬取失败: {url}")
                raise
                
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    return None
