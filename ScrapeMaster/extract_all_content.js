// 从当前页面提取所有可能包含联系方式的内容
function extractAllContentWithContacts() {
  console.log('🔍 提取页面所有内容...');
  
  // 获取完整页面文本
  const pageText = document.body.innerText;
  const lines = pageText.split('\n').filter(line => line.trim().length > 0);
  
  // 需要排除的测试数据
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
      /[电☎️📞]话[:：\s]*(\d{7,})/gi,
      /手机[号]?[:：\s]*(\d{7,})/gi,
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
  
  const results = {
    userInfo: {},
    allNotes: [],
    allContacts: [],
    potentialContactLines: [],
    excludedContacts: [],
    statistics: {
      totalLines: lines.length,
      noteLines: 0,
      contactLines: 0
    }
  };
  
  // 1. 提取用户信息
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
    if (line.includes('关注・')) {
      results.userInfo.following = line.split('关注・')[1]?.split(' ')[0];
    }
    if (line.includes('获赞与收藏・')) {
      results.userInfo.likes = line.split('获赞与收藏・')[1]?.split(' ')[0];
    }
  });
  
  // 2. 提取所有笔记标题和内容
  for (let i = 0; i < lines.length - 2; i++) {
    const currentLine = lines[i];
    const nextLine = lines[i+1];
    const nextNextLine = lines[i+2];
    
    // 笔记标题模式：标题 + Sharon多伦多地产 + 数字（点赞数）
    if (nextLine && nextLine.includes('Sharon多伦多地产') && /^\d+$/.test(nextNextLine)) {
      const note = {
        title: currentLine.trim(),
        author: nextLine.trim(),
        likes: parseInt(nextNextLine.trim()) || 0,
        fullText: `${currentLine}\n${nextLine}\n${nextNextLine}`,
        lineIndex: i
      };
      
      results.allNotes.push(note);
      results.statistics.noteLines++;
      
      // 跳过已处理的几行
      i += 2;
    }
  }
  
  // 3. 在所有行中查找联系方式
  lines.forEach((line, index) => {
    const lineLower = line.toLowerCase();
    
    // 跳过明显不是联系方式的行
    if (lineLower.includes('沪icp备') || lineLower.includes('营业执照') || 
        lineLower.includes('地址：') || lineLower.includes('电话：9501') ||
        lineLower.includes('违法不良信息举报电话')) {
      return;
    }
    
    const contacts = {};
    let hasExcluded = false;
    
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
              hasExcluded = true;
              results.excludedContacts.push({
                type: type,
                value: value,
                line: line,
                lineIndex: index,
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
      
      const contactInfo = {
        line: line,
        lineIndex: index,
        context: context,
        contacts: contacts,
        hasExcluded: hasExcluded
      };
      
      results.allContacts.push(contactInfo);
      results.statistics.contactLines++;
      
      // 如果是潜在的真实联系方式（没有排除项）
      if (!hasExcluded) {
        results.potentialContactLines.push(contactInfo);
      }
    }
  });
  
  console.log(`📊 提取完成:`);
  console.log(`   用户信息: ${Object.keys(results.userInfo).length} 项`);
  console.log(`   笔记数量: ${results.allNotes.length}`);
  console.log(`   所有联系方式行: ${results.allContacts.length}`);
  console.log(`   潜在联系方式: ${results.potentialContactLines.length}`);
  console.log(`   排除的测试数据: ${results.excludedContacts.length}`);
  
  return results;
}

// 执行提取
const extractionResults = extractAllContentWithContacts();
console.log('提取结果:', extractionResults);

// 返回结果
return extractionResults;