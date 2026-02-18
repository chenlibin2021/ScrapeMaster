// 从小红书页面提取真实联系方式的JavaScript代码
function extractRealContactsFromPage() {
  // 排除的测试数据
  const EXCLUDED_CONTACTS = {
    phone: ['6471234567', '647-123-4567', '4169876543', '416-987-6543', '13800138000', '16471234567', '9501-3888', '4006676810'],
    wechat: ['toronto_agent123', 'realtor_2024', 'canadahome', 'home_toronto', '多伦多买房咨询'],
    email: ['info@torontorealestate.ca', 'agent@torontorealestate.com', 'info@canadahomes.ca', 'contact@example.com'],
    whatsapp: ['+16471234567', '+164712345', '+1 416 987 6543', '+8613800138000'],
  };
  
  // 联系方式正则表达式
  const PATTERNS = {
    wechat: [
      /(?:微信|微[信xX]|wx|wechat)[:：\s联系]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{2,30})/gi,
      /加[我]?[微V][信xX][:：\s]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{2,30})/gi,
      /微[信xX][:：\s]*([a-zA-Z0-9_.\u4e00-\u9fa5-]{2,30})/gi,
    ],
    phone: [
      /\b(1[3-9]\d{9})\b/g,
      /\b(\d{3}[-\s]?\d{3}[-\s]?\d{4})\b/g,
      /[电☎️📞]话[:：\s]*(\d{3,})/gi,
      /手机[号]?[:：\s]*(\d{3,})/gi,
    ],
    whatsapp: [
      /(?:whatsapp|wa|WhatsApp)[:：\s联系]*([+]\d[\d\s-]{8,})/gi,
      /\bwa[:：\s]*([+]\d[\d\s-]{8,})/gi,
    ],
    email: [
      /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/gi,
      /邮箱[:：\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/gi,
    ],
  };
  
  // 获取页面文本
  const pageText = document.body.innerText;
  const lines = pageText.split('\n').filter(line => line.trim().length > 0);
  
  const results = {
    userInfo: {},
    notes: [],
    potentialContacts: [],
    excludedContacts: []
  };
  
  // 提取用户信息
  lines.forEach(line => {
    if (line.includes('Sharon多伦多地产') && line.length < 50) {
      results.userInfo.username = line;
    }
    if (line.includes('小红书号：')) {
      results.userInfo.xhsId = line.replace('小红书号：', '').trim();
    }
    if (line.includes('粉丝・')) {
      results.userInfo.fans = line.split('粉丝・')[1]?.split(' ')[0];
    }
    if (line.includes('笔记・')) {
      results.userInfo.notes = line.split('笔记・')[1]?.split(' ')[0];
    }
  });
  
  // 提取笔记标题（简化版）
  for (let i = 0; i < lines.length - 2; i++) {
    if (lines[i+1]?.includes('Sharon多伦多地产') && /^\d+$/.test(lines[i+2])) {
      const title = lines[i].trim();
      if (title && title.length > 5 && !results.notes.includes(title)) {
        results.notes.push(title);
      }
    }
  }
  
  // 提取联系方式
  lines.forEach((line, index) => {
    const lineLower = line.toLowerCase();
    
    // 跳过明显不是联系方式的行
    if (lineLower.includes('沪icp备') || lineLower.includes('营业执照') || 
        lineLower.includes('地址：') || lineLower.includes('电话：9501')) {
      return;
    }
    
    const contacts = {};
    
    // 检查各种联系方式
    for (const [type, patterns] of Object.entries(PATTERNS)) {
      const found = [];
      
      for (const pattern of patterns) {
        const matches = [...line.matchAll(pattern)];
        for (const match of matches) {
          if (match[1]) {
            const value = match[1].trim();
            
            // 检查是否在排除列表中
            const isExcluded = EXCLUDED_CONTACTS[type]?.some(excluded => 
              value.includes(excluded) || excluded.includes(value)
            );
            
            if (!isExcluded && value) {
              found.push(value);
            } else if (isExcluded) {
              results.excludedContacts.push({
                type: type,
                value: value,
                reason: '测试数据'
              });
            }
          }
        }
      }
      
      if (found.length > 0) {
        contacts[type] = [...new Set(found)]; // 去重
      }
    }
    
    if (Object.keys(contacts).length > 0) {
      // 添加上下文
      const contextStart = Math.max(0, index - 1);
      const contextEnd = Math.min(lines.length, index + 2);
      const context = lines.slice(contextStart, contextEnd).join('\n');
      
      results.potentialContacts.push({
        line: line,
        context: context,
        contacts: contacts
      });
    }
  });
  
  return results;
}

// 执行提取
const results = extractRealContactsFromPage();
console.log('📊 提取结果:', results);

// 返回结果
return results;