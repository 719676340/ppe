const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
        LevelFormat } = require('docx');
const fs = require('fs');

// 常量定义
const DXA_PER_INCH = 1440;
const A4_WIDTH = 11906;
const A4_HEIGHT = 16838;
const CONTENT_WIDTH = 9360; // A4减去边距

// 边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

// 创建标题
function createTitle(text, level = 1) {
    const fontSize = level === 1 ? 32 : (level === 2 ? 28 : 24);
    const headingLevel = level === 1 ? HeadingLevel.HEADING_1 :
                        (level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3);

    return new Paragraph({
        heading: headingLevel,
        alignment: AlignmentType.CENTER,
        children: [new TextRun({
            text: text,
            font: "SimSun",
            size: fontSize,
            bold: true,
        })],
    });
}

// 创建普通段落
function createParagraph(text, bold = false) {
    return new Paragraph({
        children: [new TextRun({
            text: text,
            font: "SimSun",
            size: 24,
            bold: bold,
        })],
        spacing: { before: 100, after: 100 },
    });
}

// 创建表格行
function createTableRow(cells) {
    return new TableRow({
        children: cells.map(text => new TableCell({
            width: { size: CONTENT_WIDTH / cells.length, type: WidthType.DXA },
            borders,
            shading: { fill: "FFFFFF", type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
                children: [new TextRun({
                    text: text,
                    font: "SimSun",
                    size: 21,
                })],
            })],
        })),
    });
}

// 创建表格
function createTable(headers, rows) {
    return new Table({
        width: { size: CONTENT_WIDTH, type: WidthType.DXA },
        columnWidths: Array(headers.length).fill(CONTENT_WIDTH / headers.length),
        rows: [
            createTableRow(headers),
            ...rows.map(row => createTableRow(row)),
        ],
    });
}

// 用户手册内容
const userManualContent = {
    title: "制丝车间安全头盔智能检测系统 用户手册",
    sections: [
        {
            title: "第一章 软件简介",
            content: [
                "1.1 软件概述",
                "",
                "制丝车间安全头盔智能检测系统是专为广西中烟南宁卷烟厂制丝车间设计的智能安全检测系统。系统采用先进的深度学习技术，通过摄像头实时监控车间重点安全区域，自动检测工人是否按规定佩戴安全帽，对违规行为进行记录和报警，帮助企业管理者提高安全生产管理水平。",
                "",
                "1.2 应用场景",
                "",
                "• 制丝车间重点安全区域监控",
                "• 生产现场安全帽佩戴检查",
                "• 安全生产违规行为记录",
                "• 安全管理数据分析",
                "",
                "1.3 系统特点",
                "",
                "• 非接触式检测：无需人工干预，自动完成检测",
                "• 实时报警：违规行为及时发现，实时推送通知",
                "• 智能去重：避免重复记录，提高数据质量",
                "• 数据统计：多维度统计分析，辅助管理决策",
                "• 易于部署：支持多种摄像头接入，部署灵活",
            ],
        },
        {
            title: "第二章 功能概述",
            content: [
                "2.1 系统功能架构",
                "",
                "本系统主要由以下功能模块组成：",
            ],
            table: {
                headers: ["功能模块", "功能描述"],
                rows: [
                    ["摄像头管理", "管理摄像头信息，配置视频源"],
                    ["区域管理", "配置检测区域，绘制检测范围"],
                    ["实时监控", "实时查看视频流和检测结果"],
                    ["违规管理", "查看和管理违规记录"],
                    ["统计分析", "查看各类统计数据和趋势图表"],
                    ["通知中心", "接收和查看系统通知"],
                ],
            },
        },
        {
            title: "第三章 安装部署",
            content: [
                "3.1 系统要求",
                "",
                "硬件要求：",
                "• CPU: Intel Core i5及以上",
                "• 内存: 8GB及以上，推荐16GB",
                "• 硬盘: 100GB可用空间，推荐SSD 256GB",
                "• 网络: 100Mbps及以上",
                "",
                "软件要求：",
                "• 操作系统: Windows 10/11、Linux (Ubuntu 20.04+)",
                "• Python 3.9或更高版本",
                "• Node.js 16或更高版本",
                "• 浏览器: Chrome 90+、Edge 90+、Firefox 88+",
                "",
                "3.2 安装步骤",
                "",
                "后端安装：",
                "1. 解压安装包，进入backend目录",
                "2. 创建虚拟环境并激活",
                "3. 安装依赖: pip install -r requirements.txt",
                "4. 配置环境变量（编辑.env文件）",
                "5. 启动后端服务: python -m uvicorn main:app --host 0.0.0.0 --port 8000",
                "",
                "前端安装：",
                "1. 进入frontend目录",
                "2. 安装依赖: npm install",
                "3. 启动开发服务器: npm run dev",
                "4. 访问 http://localhost:5173",
            ],
        },
        {
            title: "第四章 主要功能说明",
            content: [
                "4.1 摄像头管理",
                "",
                "添加摄像头：",
                "1. 点击左侧菜单'摄像头管理'",
                "2. 点击'添加摄像头'按钮",
                "3. 填写摄像头信息：",
                "   • 摄像头名称：如'制丝车间1号机'",
                "   • 视频源地址：如'rtsp://192.168.1.100:554/stream'",
                "   • 是否启用：勾选表示自动启动检测",
                "4. 点击'确定'保存",
                "",
                "4.2 区域管理",
                "",
                "添加检测区域：",
                "1. 点击左侧菜单'区域管理'",
                "2. 选择要添加区域的摄像头",
                "3. 点击'添加区域'按钮",
                "4. 在视频画面上点击绘制检测区域（至少3个点）",
                "5. 填写区域名称，如'1号机工作区'",
                "6. 点击'确定'保存",
                "",
                "4.3 实时监控",
                "",
                "查看实时监控：",
                "1. 点击左侧菜单'实时监控'",
                "2. 选择要查看的摄像头",
                "3. 系统显示实时视频流和检测结果：",
                "   • 绿色框：已佩戴安全帽",
                "   • 红色框：未佩戴安全帽（违规）",
                "   • 黄色多边形：检测区域",
                "",
                "4.4 违规管理",
                "",
                "查看违规记录：",
                "1. 点击左侧菜单'违规管理'",
                "2. 系统显示所有违规记录列表",
                "3. 每条记录包含违规时间、摄像头名称、区域名称、违规截图、处理状态",
                "",
                "导出数据：",
                "1. 设置筛选条件",
                "2. 点击'导出Excel'按钮",
                "3. 系统生成包含截图的Excel文件",
                "4. 下载保存到本地",
            ],
        },
        {
            title: "第五章 操作步骤",
            content: [
                "5.1 首次使用流程",
                "",
                "1. 安装部署：按照第三章完成系统安装",
                "2. 添加摄像头：接入车间监控摄像头",
                "3. 配置检测区域：为每个摄像头绘制检测区域",
                "4. 启动检测：启动摄像头检测",
                "5. 查看监控：进入实时监控页面查看检测效果",
                "",
                "5.2 日常使用流程",
                "",
                "1. 登录系统",
                "2. 查看实时监控",
                "3. 处理违规通知",
                "4. 查看统计数据",
                "5. 导出分析报告",
                "",
                "5.3 违规处理流程",
                "",
                "1. 收到违规通知",
                "2. 查看违规截图和详情",
                "3. 核实违规情况",
                "4. 通知相关责任人",
                "5. 跟踪整改情况",
                "6. 标记违规记录为已处理",
            ],
        },
        {
            title: "第六章 注意事项",
            content: [
                "6.1 使用注意事项",
                "",
                "• 摄像头位置：确保摄像头能够清晰覆盖检测区域",
                "• 光照条件：保持充足且稳定的光照条件",
                "• 网络带宽：确保网络带宽充足，避免视频卡顿",
                "• 定期检查：定期检查系统运行状态和检测效果",
                "",
                "6.2 检测效果优化建议",
                "",
                "• 区域绘制：检测区域应尽量贴近实际工作区域",
                "• 角度调整：摄像头角度应垂直或略微俯视",
                "• 背景简洁：检测区域内应避免复杂背景",
                "• 距离控制：摄像头与检测区域的距离不宜过远",
                "",
                "6.3 数据备份建议",
                "",
                "• 定期备份违规记录数据库",
                "• 定期备份违规截图文件",
                "• 建议至少保留6个月的历史数据",
            ],
        },
        {
            title: "第七章 常见问题",
            content: [
                "Q1：检测不准确怎么办？",
                "",
                "可能原因及解决方法：",
                "• 检查摄像头是否清晰覆盖检测区域",
                "• 调整检测区域范围",
                "• 检查光照条件是否良好",
                "• 联系技术支持进行模型优化",
                "",
                "Q2：视频流无法连接怎么办？",
                "",
                "请检查：",
                "• 摄像头网络连接是否正常",
                "• 视频源地址是否正确",
                "• 防火墙是否允许访问",
                "• 摄像头是否支持该视频流协议",
                "",
                "Q3：系统提示内存不足怎么办？",
                "",
                "解决方法：",
                "• 减少同时检测的摄像头数量",
                "• 降低视频分辨率",
                "• 增加服务器内存",
            ],
        },
        {
            title: "第八章 技术支持",
            content: [
                "如遇到本手册未能解决的问题，请联系技术支持：",
                "",
                "• 技术支持电话：（待填写）",
                "• 技术支持邮箱：（待填写）",
                "• 技术支持地址：（待填写）",
            ],
        },
    ],
};

// 创建文档
function createUserManual() {
    const children = [];

    // 标题页
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({
            text: userManualContent.title,
            font: "SimHei",
            size: 44,
            bold: true,
        })],
    }));

    children.push(createParagraph("著作权人：（待填写）"));
    children.push(createParagraph("版本：1.0"));
    children.push(createParagraph("更新日期：2024年12月"));

    // 添加分页
    children.push(new Paragraph({
        children: [],
    }));

    // 添加章节
    userManualContent.sections.forEach(section => {
        children.push(createTitle(section.title, 2));
        children.push(new Paragraph({ text: "" }));

        if (section.content) {
            section.content.forEach(line => {
                if (line.startsWith("• ")) {
                    children.push(createParagraph("  " + line));
                } else if (line.match(/^\d+\./)) {
                    children.push(createParagraph(line));
                } else if (line) {
                    children.push(createParagraph(line));
                } else {
                    children.push(new Paragraph({ text: "" }));
                }
            });
        }

        if (section.table) {
            children.push(createTable(section.table.headers, section.table.rows));
        }

        children.push(new Paragraph({ text: "" }));
    });

    return new Document({
        styles: {
            default: {
                document: {
                    run: { font: "SimSun", size: 24 },
                },
            },
            paragraphStyles: [
                {
                    id: "Heading1",
                    name: "Heading 1",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 32, bold: true, font: "SimHei" },
                    paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 },
                },
                {
                    id: "Heading2",
                    name: "Heading 2",
                    basedOn: "Normal",
                    next: "Normal",
                    quickFormat: true,
                    run: { size: 28, bold: true, font: "SimHei" },
                    paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 },
                },
            ],
        },
        sections: [{
            properties: {
                page: {
                    size: { width: A4_WIDTH, height: A4_HEIGHT },
                    margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
                },
            },
            children,
        }],
    });
}

// 保存文档
Packer.toBuffer(createUserManual()).then(buffer => {
    const outputPath = "/Users/heqijie/个人项目/中烟软著/头盔/copyright-application-materials/用户手册_模板版.docx";
    fs.writeFileSync(outputPath, buffer);
    console.log(`✓ 已生成: ${outputPath}`);
}).catch(err => {
    console.error("生成失败:", err);
});
