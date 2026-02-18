// 访问小红书笔记页面的JavaScript代码
function accessNotePage() {
  console.log('🔍 尝试访问笔记页面...');
  
  // 方法1: 通过模拟点击笔记卡片
  const noteCards = Array.from(document.querySelectorAll('div, article, section')).filter(el => {
    const text = el.innerText || '';
    return text.includes('Sharon多伦多地产') && text.includes('\n') && /\d+/.test(text);
  });
  
  if (noteCards.length > 0) {
    console.log(`找到 ${noteCards.length} 个笔记卡片`);
    
    // 点击第一个笔记卡片
    const firstNote = noteCards[0];
    console.log('点击第一个笔记卡片:', firstNote.innerText.substring(0, 50));
    
    // 尝试触发点击事件
    const clickEvent = new MouseEvent('click', {
      view: window,
      bubbles: true,
      cancelable: true
    });
    firstNote.dispatchEvent(clickEvent);
    
    // 也尝试直接调用click方法
    firstNote.click();
    
    return { success: true, method: 'noteCardClick', count: noteCards.length };
  }
  
  // 方法2: 通过链接查找
  const links = Array.from(document.querySelectorAll('a')).filter(link => {
    const href = link.href || '';
    const text = link.innerText || '';
    
    // 查找笔记相关链接
    return (
      href.includes('/explore/') ||
      href.includes('/search_result/') ||
      (text.length > 10 && !text.includes('沪ICP备') && !text.includes('营业执照'))
    );
  });
  
  if (links.length > 0) {
    console.log(`找到 ${links.length} 个可能链接`);
    
    // 查找第一个看起来像笔记的链接
    const noteLink = links.find(link => {
      const text = link.innerText || '';
      return text.includes('Sharon多伦多地产') || /\d+/.test(text);
    }) || links[0];
    
    console.log('点击链接:', noteLink.href);
    noteLink.click();
    
    return { success: true, method: 'linkClick', href: noteLink.href };
  }
  
  // 方法3: 通过滚动加载更多内容
  console.log('尝试滚动加载...');
  window.scrollTo(0, document.body.scrollHeight);
  
  // 等待内容加载
  setTimeout(() => {
    console.log('滚动完成，重新尝试查找');
    // 这里可以递归调用，但为了避免无限循环，先返回
  }, 2000);
  
  return { success: false, reason: '未找到可点击的笔记元素' };
}

// 执行访问
const result = accessNotePage();
console.log('访问结果:', result);

// 返回结果供外部使用
return result;