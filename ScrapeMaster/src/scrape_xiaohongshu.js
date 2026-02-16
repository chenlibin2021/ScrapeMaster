#!/usr/bin/env node
/**
 * 小红书评论爬虫 - Node.js版本
 * 使用Puppeteer连接到Chrome
 */

const fs = require('fs');
const XLSX = require('xlsx');

// 联系方式检测正则
const CONTACT_PATTERNS = {
    wechat: [
        /[微V信][信xX][:：\s]*([a-zA-Z0-9_-]{5,20})/gi,
        /wx[:：\s]*([a-zA-Z0-9_-]{5,20})/gi,
        /加我?[微V][信xX]/gi,
        /扫码加[微V]/gi,
    ],
    phone: [
        /(\d{3}[-\s]?\d{3}[-\s]?\d{4})/g,  // 北美
        /(\d{3}[-\s]?\d{4}[-\s]?\d{4})/g,  // 中国
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

async function scrapeComments(page, maxNotes = 10) {
    const results = [];
    
    try {
        // 访问Sharon主页
        const sharonUrl = 'https://www.xiaohongshu.com/user/profile/59e2f0de153c3c1961a1deb4';
        console.log('📍 访问 Sharon 主页...');
        await page.goto(sharonUrl, { waitUntil: 'networkidle2', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        // 滚动加载笔记
        console.log('📜 滚动加载笔记列表...');
        for (let i = 0; i < 5; i++) {
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await page.waitForTimeout(2000);
        }
        
        // 获取笔记链接
        const noteLinks = await page.evaluate(() => {
            const links = new Set();
            document.querySelectorAll('a[href*="/explore/"]').forEach(el => {
                const href = el.getAttribute('href');
                if (href && href.includes('/explore/')) {
                    const fullUrl = href.startsWith('http') ? href : 'https://www.xiaohongshu.com' + href;
                    links.add(fullUrl);
                }
            });
            return Array.from(links);
        });
        
        console.log(`✅ 找到 ${noteLinks.length} 条笔记`);
        const targetNotes = noteLinks.slice(0, maxNotes);
        console.log(`📌 处理前 ${targetNotes.length} 条`);
        
        // 遍历笔记
        for (let idx = 0; idx < targetNotes.length; idx++) {
            const noteUrl = targetNotes[idx];
            console.log(`\n[${idx + 1}/${targetNotes.length}] 处理笔记: ${noteUrl}`);
            
            try {
                await page.goto(noteUrl, { waitUntil: 'networkidle2', timeout: 30000 });
                await page.waitForTimeout(3000);
                
                // 获取标题
                const noteTitle = await page.evaluate(() => {
                    const titleEl = document.querySelector('h1, .title, [class*="title"]');
                    return titleEl ? titleEl.innerText : '无标题';
                }) || '无标题';
                
                console.log(`  📝 标题: ${noteTitle.substring(0, 50)}...`);
                
                // 滚动加载评论
                console.log(`  💬 加载评论...`);
                for (let i = 0; i < 3; i++) {
                    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
                    await page.waitForTimeout(1500);
                }
                
                // 提取评论
                const comments = await page.evaluate(() => {
                    const results = [];
                    const commentEls = document.querySelectorAll('[class*="comment"], .note-item, [class*="Comment"]');
                    
                    commentEls.forEach(el => {
                        const userEl = el.querySelector('[class*="user"], [class*="name"], .author');
                        const contentEl = el.querySelector('[class*="content"], [class*="text"], p');
                        const timeEl = el.querySelector('[class*="time"], [class*="date"], time');
                        
                        if (contentEl && contentEl.innerText.trim()) {
                            results.push({
                                user: userEl ? userEl.innerText.trim() : '未知用户',
                                content: contentEl.innerText.trim(),
                                time: timeEl ? timeEl.innerText.trim() : ''
                            });
                        }
                    });
                    
                    return results;
                });
                
                console.log(`  📊 提取到 ${comments.length} 条评论`);
                
                // 过滤评论
                let filtered = 0;
                for (const comment of comments) {
                    const { has, types } = hasContactInfo(comment.content);
                    
                    if (has) {
                        filtered++;
                        const contactDetails = extractContactDetails(comment.content);
                        
                        results.push({
                            '笔记标题': noteTitle,
                            '笔记链接': noteUrl,
                            '用户名': comment.user,
                            '评论内容': comment.content,
                            '评论时间': comment.time,
                            '联系方式类型': types.join(', '),
                            '提取的联系方式': JSON.stringify(contactDetails),
                            '抓取时间': new Date().toISOString()
                        });
                    }
                }
                
                if (filtered > 0) {
                    console.log(`  ✅ 发现 ${filtered} 条包含联系方式的评论`);
                } else {
                    console.log(`  ⚠️  未发现包含联系方式的评论`);
                }
                
                // 随机延迟
                await page.waitForTimeout(2000 + Math.random() * 2000);
                
            } catch (err) {
                console.log(`  ❌ 处理笔记出错: ${err.message}`);
            }
        }
        
    } catch (err) {
        console.error(`❌ 抓取出错: ${err.message}`);
    }
    
    return results;
}

async function main() {
    console.log('='.repeat(60));
    console.log('小红书评论爬虫 - Sharon多伦多地产');
    console.log('目标：抓取包含联系方式的评论');
    console.log('='.repeat(60));
    
    const puppeteer = require('puppeteer-core');
    
    console.log('\n🔗 连接到Chrome浏览器...');
    
    let browser;
    try {
        browser = await puppeteer.connect({
            browserURL: 'http://127.0.0.1:18792'
        });
        
        const pages = await browser.pages();
        const page = pages[0];
        
        console.log('✅ 连接成功');
        console.log('\n🚀 开始抓取（测试模式：前10条笔记）...');
        
        const results = await scrapeComments(page, 10);
        
        if (results.length > 0) {
            // 保存为Excel
            const ws = XLSX.utils.json_to_sheet(results);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, '评论数据');
            
            const filename = `/home/chenlibin/.openclaw/workspace/sharon_comments_${Date.now()}.xlsx`;
            XLSX.writeFile(wb, filename);
            
            console.log(`\n🎉 成功！`);
            console.log(`📁 文件已保存: ${filename}`);
            console.log(`📊 总共找到 ${results.length} 条包含联系方式的评论`);
            
            // 统计
            const typeCounts = {};
            results.forEach(r => {
                const types = r['联系方式类型'].split(', ');
                types.forEach(t => {
                    typeCounts[t] = (typeCounts[t] || 0) + 1;
                });
            });
            
            console.log('\n📈 联系方式分布:');
            Object.entries(typeCounts)
                .sort((a, b) => b[1] - a[1])
                .forEach(([type, count]) => {
                    console.log(`  - ${type}: ${count} 条`);
                });
        } else {
            console.log('\n⚠️  未找到包含联系方式的评论');
        }
        
    } catch (err) {
        console.error(`❌ 错误: ${err.message}`);
    } finally {
        if (browser) {
            await browser.disconnect();
        }
    }
}

main();
