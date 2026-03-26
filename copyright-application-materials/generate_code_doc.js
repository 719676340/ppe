const { Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel } = require('docx');
const fs = require('fs');
const path = require('path');

const A4_WIDTH = 11906;
const A4_HEIGHT = 16838;

// 源代码文件列表（按重要性排序）
const sourceFiles = [
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/main.py", name: "main.py - 主程序入口" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/config.py", name: "config.py - 系统配置" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/detection/detector.py", name: "detection/detector.py - PPE检测器" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/detection/stream_processor.py", name: "detection/stream_processor.py - 视频流处理器" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/detection/violation_recorder.py", name: "detection/violation_recorder.py - 违规记录器" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/detection/roi_manager.py", name: "detection/roi_manager.py - 区域管理器" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/database.py", name: "management/database.py - 数据库模型" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/routers/camera.py", name: "management/routers/camera.py - 摄像头API" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/routers/violation.py", name: "management/routers/violation.py - 违规管理API" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/routers/statistics.py", name: "management/routers/statistics.py - 统计分析API" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/services/violation_service.py", name: "management/services/violation_service.py - 违规服务" },
    { path: "/Users/heqijie/个人项目/中烟软著/头盔/backend/management/services/statistics_service.py", name: "management/services/statistics_service.py - 统计服务" },
];

function createFileHeader(fileName, lineCount) {
    return new Paragraph({
        alignment: AlignmentType.LEFT,
        spacing: { before: 200, after: 100 },
        children: [
            new TextRun({
                text: "═══════════════════════════════════════════════════════════════",
                font: "SimSun",
                size: 20,
                color: "666666",
            }),
            new TextRun({
                text: "\n" + fileName + " (" + lineCount + " 行)",
                font: "SimHei",
                size: 22,
                bold: true,
            }),
        ],
    });
}

function createCodeLine(lineNumber, code) {
    const lineNum = String(lineNumber).padStart(4, ' ');
    return new Paragraph({
        children: [
            new TextRun({
                text: lineNum + " ",
                font: "Consolas",
                size: 18,
                color: "666666",
            }),
            new TextRun({
                text: code || " ",
                font: "Consolas",
                size: 18,
            }),
        ],
        spacing: { before: 0, after: 0 },
        indent: { left: 300 },
    });
}

function createPageNumber(pageNum) {
    return new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 100, after: 200 },
        children: [
            new TextRun({
                text: "--- 第 " + pageNum + " 页 ---",
                font: "SimSun",
                size: 20,
                color: "999999",
            }),
        ],
    });
}

function readSourceCode(filePath) {
    try {
        return fs.readFileSync(filePath, 'utf-8');
    } catch (err) {
        console.error("无法读取文件:", filePath, err.message);
        return null;
    }
}

function createCodeDocument() {
    const children = [];
    let currentPage = 1;
    let linesOnCurrentPage = 0;
    const linesPerPage = 50;

    // 标题
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({
            text: "制丝车间安全头盔智能检测系统 源代码文档",
            font: "SimHei",
            size: 44,
            bold: true,
        })],
    }));

    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 200 },
        children: [new TextRun({
            text: "著作权人：（待填写）",
            font: "SimSun",
            size: 24,
        })],
    }));

    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({
            text: "版本：1.0",
            font: "SimSun",
            size: 24,
        })],
    }));

    // 前半部分：从前往后展示代码
    children.push(createPageNumber(currentPage++));
    linesOnCurrentPage = 0;

    for (const file of sourceFiles) {
        const code = readSourceCode(file.path);
        if (!code) continue;

        const lines = code.split('\n');
        const fileLineCount = lines.length;

        // 文件头
        children.push(createFileHeader(file.name, fileLineCount));
        linesOnCurrentPage += 2;

        // 代码行
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];

            // 检查是否需要新页面
            if (linesOnCurrentPage >= linesPerPage) {
                children.push(createPageNumber(currentPage++));
                linesOnCurrentPage = 0;
            }

            children.push(createCodeLine(i + 1, line));
            linesOnCurrentPage++;
        }

        // 文件间空行
        children.push(new Paragraph({ text: "" }));
        linesOnCurrentPage++;

        // 如果已达到30页，开始后半部分
        if (currentPage > 30) {
            break;
        }
    }

    // 如果前半部分不足30页，继续添加
    while (currentPage <= 30) {
        if (linesOnCurrentPage >= linesPerPage) {
            children.push(createPageNumber(currentPage++));
            linesOnCurrentPage = 0;
        } else {
            children.push(new Paragraph({ text: " " }));
            linesOnCurrentPage++;
        }
    }

    // 后半部分：继续展示剩余代码（从后往前）
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 400, after: 200 },
        children: [new TextRun({
            text: "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            font: "SimSun",
            size: 20,
            color: "666666",
        })],
    }));

    const remainingFiles = sourceFiles.slice(6); // 跳过前面已展示的文件
    for (const file of remainingFiles) {
        const code = readSourceCode(file.path);
        if (!code) continue;

        const lines = code.split('\n');
        const fileLineCount = lines.length;

        children.push(createFileHeader(file.name, fileLineCount));

        for (let i = 0; i < lines.length; i++) {
            children.push(createCodeLine(i + 1, lines[i]));
            linesOnCurrentPage++;

            if (linesOnCurrentPage >= linesPerPage) {
                children.push(createPageNumber(currentPage++));
                linesOnCurrentPage = 0;
            }
        }

        children.push(new Paragraph({ text: "" }));
        linesOnCurrentPage++;
    }

    // 添加尾页
    children.push(createPageNumber(currentPage));

    return new Document({
        styles: {
            default: {
                document: {
                    run: { font: "SimSun", size: 24 },
                },
            },
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

Packer.toBuffer(createCodeDocument()).then(buffer => {
    const outputPath = "/Users/heqijie/个人项目/中烟软著/头盔/copyright-application-materials/源代码文档_模板版.docx";
    fs.writeFileSync(outputPath, buffer);
    console.log(`✓ 已生成: ${outputPath}`);
}).catch(err => {
    console.error("生成失败:", err);
});
