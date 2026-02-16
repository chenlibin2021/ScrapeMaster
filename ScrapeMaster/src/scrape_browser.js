/**
 * 小红书评论爬虫 - 浏览器控制台版本
 * 使用方法：
 * 1. 打开 Sharon多伦多地产 的主页
 * 2. 按 F12 打开开发者工具
 * 3. 切换到 Console (控制台) 标签
 * 4. 粘贴这整个脚本
 * 5. 按回车运行
 * 6. 等待抓取完成，会自动下载Excel文件
 */

(async function() {
    console.log('='.repeat(60));
    console.log('小红书评论爬虫 - Sharon多伦多地产');
    console.log('目标：抓取包含联系方式的评论');
    console.log('='.repeat(60));
    
    // 联系方式检测正则
    const CONTACT_PATTERNS = {
        wechat: [
            /[微V信][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})/gi,
            /wx[:：\s]*([a-zA-Z0-9_-]{5,20})/gi,
            /加我?[微V][信xX]/gi,
            /扫码加[微V]/gi,
        ],
        phone: [
            /(\d{3}[-\s]?\d{3}[-\s]?\d{4})/g,
            /(\d{3}[-\s]?\d{4}[-\s]?\d{4})/g,
            /[电☎️📞]话[:：\s]*(\d[\d\s-]{7,})/g,
        ],
        qq: [
            /QQ[:：\s]*(\d{5,11})/gi,
            /[扣抠][:：\s]*(\d{5,11})/gi,
        ],
        email: [
            /([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g,
        ],
        whatsapp: [
            /whatsapp[:：\s]*([+\d\s-]{10,})/gi,
            /wa[:：\s]*([+\d\s-]{10,})/gi,
        ],
    };
    
    function hasContactInfo(text) {
        if (!text) return { has: false, types: [] };
        
        const foundTypes = [];
        for (const [contactType, patterns] of Object.entries(CONTACT_PATTERNS)) {
            for (const pattern of patterns) {
                if (pattern.test(text)) {
                    foundTypes.push(contactType);
                    break;
                }
            }
        }
        
        return { has: foundTypes.length > 0, types: foundTypes };
    }
    
    function extractContactDetails(text) {
        const contacts = {};
        
        for (const [contactType, patterns] of Object.entries(CONTACT_PATTERNS)) {
            for (const pattern of patterns) {
                const matches = text.match(pattern);
                if (matches) {
                    if (!contacts[contactType]) contacts[contactType] = [];
                    contacts[contactType].push(...matches);
                }
            }
        }
        
        return contacts;
    }
    
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async function scrapeCurrentPage() {
        console.log('📍 当前页面:', window.location.href);
        
        // 滚动加载笔记
        console.log('📜 滚动加载笔记列表...');
        for (let i = 0; i < 5; i++) {
            window.scrollTo(0, document.body.scrollHeight);
            await sleep(2000);
        }
        
        // 获取笔记链接
        const noteLinks = [];
        document.querySelectorAll('a[href*="/explore/"]').forEach(el => {
            const href = el.getAttribute('href');
            if (href && href.includes('/explore/')) {
                const fullUrl = href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href;
                if (!noteLinks.includes(fullUrl)) {
                    noteLinks.push(fullUrl);
                }
            }
        });
        
        console.log(`✅ 找到 ${noteLinks.length} 条笔记`);
        
        // 限制数量（测试）
        const MAX_NOTES = 10;
        const targetNotes = noteLinks.slice(0, MAX_NOTES);
        console.log(`📌 将处理前 ${targetNotes.length} 条笔记`);
        
        const results = [];
        
        // 遍历笔记
        for (let idx = 0; idx < targetNotes.length; idx++) {
            const noteUrl = targetNotes[idx];
            console.log(`\n[${idx + 1}/${targetNotes.length}] 处理笔记...`);
            
            try {
                // 在新标签页打开
                const newTab = window.open(noteUrl, '_blank');
                await sleep(5000); // 等待加载
                
                // 注意：跨标签页访问有限制，这里改用直接访问
                window.location.href = noteUrl;
                await sleep(4000);
                
                // 获取标题
                const titleEl = document.querySelector('h1, .title, [class*="title"]');
                const noteTitle = titleEl ? titleEl.innerText : '无标题';
                
                console.log(`  📝 标题: ${noteTitle.substring(0, 50)}...`);
                
                // 滚动加载评论
                console.log(`  💬 加载评论...`);
                for (let i = 0; i < 3; i++) {
                    window.scrollTo(0, document.body.scrollHeight);
                    await sleep(1500);
                }
                
                // 点击展开按钮
                document.querySelectorAll('button').forEach(btn => {
                    if (btn.innerText.includes('展开') || btn.innerText.includes('更多')) {
                        try { btn.click(); } catch(e) {}
                    }
                });
                await sleep(1000);
                
                // 提取评论
                const commentEls = document.querySelectorAll('[class*="comment"], .note-item, [class*="Comment"]');
                
                console.log(`  📊 找到 ${commentEls.length} 个评论元素`);
                
                let filtered = 0;
                commentEls.forEach(el => {
                    const userEl = el.querySelector('[class*="user"], [class*="name"], .author');
                    const contentEl = el.querySelector('[class*="content"], [class*="text"], p');
                    const timeEl = el.querySelector('[class*="time"], [class*="date"], time');
                    
                    if (contentEl && contentEl.innerText.trim()) {
                        const content = contentEl.innerText.trim();
                        const { has, types } = hasContactInfo(content);
                        
                        if (has) {
                            filtered++;
                            const contactDetails = extractContactDetails(content);
                            
                            results.push({
                                '笔记标题': noteTitle,
                                '笔记链接': noteUrl,
                                '用户名': userEl ? userEl.innerText.trim() : '未知用户',
                                '评论内容': content,
                                '评论时间': timeEl ? timeEl.innerText.trim() : '',
                                '联系方式类型': types.join(', '),
                                '提取的联系方式': JSON.stringify(contactDetails),
                                '抓取时间': new Date().toLocaleString('zh-CN')
                            });
                        }
                    }
                });
                
                if (filtered > 0) {
                    console.log(`  ✅ 发现 ${filtered} 条包含联系方式的评论`);
                } else {
                    console.log(`  ⚠️  未发现包含联系方式的评论`);
                }
                
                // 返回主页继续
                window.history.back();
                await sleep(2000);
                
            } catch (err) {
                console.error(`  ❌ 处理笔记出错:`, err);
            }
        }
        
        return results;
    }
    
    // 由于跨标签页限制，改用简化版本：只抓取当前页面
    console.log('\n⚠️  浏览器安全限制：将只抓取当前打开的笔记页面');
    console.log('💡 建议：手动打开一条笔记，然后运行此脚本');
    console.log('\n是否继续抓取当前页面？(输入 y 继续)');
    
    // 简化版：只抓取当前笔记
    async function scrapeCurrentNote() {
        console.log('\n🚀 开始抓取当前笔记...');
        
        const noteUrl = window.location.href;
        
        // 获取标题
        const titleEl = document.querySelector('h1, .title, [class*="title"]');
        const noteTitle = titleEl ? titleEl.innerText : '无标题';
        
        console.log(`📝 标题: ${noteTitle}`);
        
        // 滚动加载评论
        console.log('💬 加载评论...');
        for (let i = 0; i < 5; i++) {
            window.scrollTo(0, document.body.scrollHeight);
            await sleep(1500);
        }
        
        // 点击展开
        let expandCount = 0;
        document.querySelectorAll('button').forEach(btn => {
            if (btn.innerText.includes('展开') || btn.innerText.includes('更多')) {
                try { 
                    btn.click(); 
                    expandCount++;
                } catch(e) {}
            }
        });
        
        if (expandCount > 0) {
            console.log(`✅ 点击了 ${expandCount} 个展开按钮`);
            await sleep(2000);
        }
        
        // 提取评论
        const results = [];
        const commentEls = document.querySelectorAll('[class*="comment"], .note-item, [class*="Comment"]');
        
        console.log(`📊 找到 ${commentEls.length} 个评论元素`);
        
        commentEls.forEach((el, idx) => {
            const userEl = el.querySelector('[class*="user"], [class*="name"], .author');
            const contentEl = el.querySelector('[class*="content"], [class*="text"], p');
            const timeEl = el.querySelector('[class*="time"], [class*="date"], time');
            
            if (contentEl && contentEl.innerText.trim()) {
                const content = contentEl.innerText.trim();
                const { has, types } = hasContactInfo(content);
                
                if (has) {
                    const contactDetails = extractContactDetails(content);
                    
                    results.push({
                        '笔记标题': noteTitle,
                        '笔记链接': noteUrl,
                        '用户名': userEl ? userEl.innerText.trim() : '未知用户',
                        '评论内容': content,
                        '评论时间': timeEl ? timeEl.innerText.trim() : '',
                        '联系方式类型': types.join(', '),
                        '提取的联系方式': JSON.stringify(contactDetails),
                        '抓取时间': new Date().toLocaleString('zh-CN')
                    });
                }
            }
        });
        
        console.log(`\n✅ 找到 ${results.length} 条包含联系方式的评论`);
        
        if (results.length > 0) {
            // 转换为CSV
            const headers = Object.keys(results[0]);
            let csv = headers.join(',') + '\n';
            
            results.forEach(row => {
                const values = headers.map(h => {
                    const val = row[h] || '';
                    // 转义逗号和引号
                    return '"' + val.replace(/"/g, '""') + '"';
                });
                csv += values.join(',') + '\n';
            });
            
            // 下载文件
            const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `sharon_comments_${Date.now()}.csv`;
            link.click();
            
            console.log('🎉 已下载CSV文件！');
            
            // 显示预览
            console.table(results.slice(0, 5));
        } else {
            console.log('⚠️  当前笔记没有包含联系方式的评论');
        }
        
        return results;
    }
    
    // 自动运行
    await scrapeCurrentNote();
    
})();
