const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType } = require('docx');
const fs = require('fs');

const DXA_PER_INCH = 1440;
const A4_WIDTH = 11906;
const A4_HEIGHT = 16838;
const CONTENT_WIDTH = 9360;

const border = { style: BorderStyle.SINGLE, size: 1, color: "000000" };
const borders = { top: border, bottom: border, left: border, right: border };

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

const designDocContent = {
    title: "制丝车间安全头盔智能检测系统 设计说明书",
    sections: [
        {
            title: "第一章 软件概述",
            content: [
                "1.1 项目背景",
                "",
                "广西中烟南宁卷烟厂制丝车间作为生产核心区域，安全生产是首要任务。根据安全规范要求，进入车间重点区域的作业人员必须佩戴安全帽。传统的人工巡检方式存在效率低、覆盖面小、难以及时发现问题等不足。",
                "",
                "为提高安全生产管理水平，制丝车间安全头盔智能检测系统采用先进的计算机视觉和深度学习技术，实现安全帽佩戴情况的自动化检测和违规行为记录，为安全生产管理提供技术支撑。",
                "",
                "1.2 建设目标",
                "",
                "• 自动化检测：实现安全帽佩戴情况的7×24小时自动检测",
                "• 实时告警：违规行为及时发现，实时推送通知",
                "• 数据记录：完整记录违规事件，便于追溯和分析",
                "• 统计分析：提供多维度统计数据，辅助管理决策",
                "• 易用性强：界面友好，操作简单，便于推广使用",
                "",
                "1.3 应用范围",
                "",
                "本系统主要应用于：",
                "• 制丝车间重点安全区域",
                "• 其他需要佩戴安全帽的生产作业区域",
                "• 建设工地等工业安全场景",
            ],
        },
        {
            title: "第二章 需求分析",
            content: [
                "2.1 功能性需求",
                "",
                "视频流处理需求：",
                "• 支持多路RTSP视频流同时接入",
                "• 支持HTTP视频流接入",
                "• 支持本地视频文件检测",
                "• 实时视频流解码和处理",
                "• 视频流断线自动重连",
                "",
                "目标检测需求：",
                "• 检测人员是否佩戴安全帽",
                "• 识别no_ppe（未佩戴）类别",
                "• 识别with_ppe（已佩戴）类别",
                "• 输出目标边界框坐标",
                "• 输出检测置信度",
                "",
                "区域管理需求：",
                "• 支持多边形检测区域绘制",
                "• 判断目标中心点是否在区域内",
                "• 支持多区域同时检测",
                "• 区域启用/禁用控制",
                "",
                "2.2 非功能性需求",
                "",
                "性能需求：",
                "• 检测延迟：≤500ms",
                "• 并发摄像头数：≥8路",
                "• 检测准确率：≥95%",
                "• 系统可用性：≥99%",
                "",
                "可靠性需求：",
                "• 系统崩溃后自动恢复",
                "• 视频流断线自动重连",
                "• 数据定期自动备份",
                "",
                "安全性需求：",
                "• 用户身份认证",
                "• 操作日志记录",
                "• 数据访问权限控制",
            ],
            table: {
                headers: ["需求编号", "需求描述", "优先级"],
                rows: [
                    ["F001", "支持多路RTSP视频流同时接入", "高"],
                    ["F002", "支持HTTP视频流接入", "高"],
                    ["F101", "检测人员是否佩戴安全帽", "高"],
                    ["F102", "识别no_ppe（未佩戴）类别", "高"],
                    ["F201", "支持多边形检测区域绘制", "高"],
                    ["F301", "自动保存违规截图", "高"],
                ],
            },
        },
        {
            title: "第三章 总体设计",
            content: [
                "3.1 系统架构设计",
                "",
                "本系统采用前后端分离的架构设计，整体分为四层：",
                "",
                "• 用户界面层：实时监控、违规管理、统计分析、系统设置",
                "• 业务逻辑层：摄像头管理、区域管理、违规处理、统计服务",
                "• 核心处理层：视频处理、PPE检测器、区域管理器、违规记录器",
                "• 数据存储层：摄像头、检测区域、违规记录、文件存储",
                "",
                "3.2 技术架构",
                "",
                "后端技术栈：",
                "• Python 3.9+ - 主要开发语言",
                "• FastAPI - Web框架",
                "• Uvicorn - ASGI服务器",
                "• SQLAlchemy - ORM框架",
                "• YOLO v11 - 目标检测模型",
                "• OpenCV - 视频处理",
                "• SQLite - 数据库",
                "",
                "前端技术栈：",
                "• Vue.js 3.x - 前端框架",
                "• Element Plus - UI组件库",
                "• ECharts - 图表库",
                "• Axios - HTTP客户端",
                "• Pinia - 状态管理",
            ],
        },
        {
            title: "第四章 详细设计",
            content: [
                "4.1 核心模块设计",
                "",
                "4.1.1 PPE检测器模块（PPEDetector）",
                "",
                "功能描述：负责对视频帧进行PPE检测，识别人员是否佩戴安全帽。",
                "",
                "主要方法：",
                "• __init__(model_path) - 初始化YOLO模型",
                "• detect(image) - 检测图像中的PPE佩戴情况",
                "• set_confidence_threshold(threshold) - 设置置信度阈值",
                "• set_iou_threshold(threshold) - 设置IOU阈值",
                "• get_center_point(bbox) - 获取边界框中心点",
                "",
                "检测流程：",
                "输入图像 → YOLO模型推理 → 后处理 → 返回检测结果",
                "              ↓",
                "        目标检测+分类",
                "        no_ppe/with_ppe",
                "",
                "4.1.2 视频流处理器模块（StreamProcessor）",
                "",
                "功能描述：负责视频流的采集、处理和检测结果管理。",
                "",
                "主要方法：",
                "• start() - 启动视频流处理",
                "• stop() - 停止视频流处理",
                "• get_latest_frame() - 获取最新处理后的帧",
                "• get_latest_detections() - 获取最新检测结果",
                "• get_status() - 获取处理器状态",
                "",
                "处理流程：",
                "视频流 → 读取帧 → PPE检测 → 区域判断 → 违规处理 → 结果推送",
                "",
                "4.1.3 ROI管理器模块（ROIManager）",
                "",
                "功能描述：管理检测区域，判断目标是否在区域内。",
                "",
                "主要方法：",
                "• parse_coordinates(coordinates_json) - 解析ROI坐标JSON字符串",
                "• scale_coordinates(normalized_coords, width, height) - 坐标归一化转换",
                "• point_in_polygon(point, polygon) - 判断点是否在多边形内（射线法）",
                "• is_bbox_in_zone(bbox, zone_coords) - 判断边界框是否在检测区域内",
                "• draw_zone(image, zone_coords) - 在图像上绘制检测区域",
                "",
                "区域判断算法：",
                "采用射线法判断点是否在多边形内：",
                "1. 从待判断点向右发射射线",
                "2. 统计射线与多边形边的交点数",
                "3. 交点数为奇数则在多边形内，偶数则在外",
                "",
                "4.1.4 违规记录器模块（ViolationRecorder）",
                "",
                "功能描述：处理违规检测和记录，包括去重、截图保存、数据库存储。",
                "",
                "去重算法：",
                "基于时间和位置的双重去重：",
                "1. 计算当前检测点与缓存中历史点的欧氏距离",
                "2. 如果距离小于阈值（默认100像素）且时间在去重窗口内（默认30秒），判定为重复",
                "3. 定期清理过期的缓存记录",
            ],
        },
        {
            title: "第五章 数据库设计",
            content: [
                "5.1 数据表设计",
                "",
                "摄像头表（camera）：",
                "• id - 主键",
                "• name - 摄像头名称",
                "• source_url - 视频源地址",
                "• enabled - 是否启用",
                "• created_at - 创建时间",
                "",
                "检测区域表（detection_zone）：",
                "• id - 主键",
                "• camera_id - 关联摄像头ID",
                "• name - 区域名称",
                "• coordinates - 区域坐标JSON",
                "• enabled - 是否启用",
                "• created_at - 创建时间",
                "",
                "违规记录表（violation）：",
                "• id - 主键",
                "• camera_id - 关联摄像头ID",
                "• zone_id - 关联区域ID",
                "• violation_time - 违规时间",
                "• image_path - 截图路径",
                "• is_processed - 是否已处理",
                "• remark - 备注",
                "• created_at - 创建时间",
                "",
                "通知表（notification）：",
                "• id - 主键",
                "• type - 通知类型",
                "• title - 通知标题",
                "• message - 通知内容",
                "• camera_id - 关联摄像头ID",
                "• zone_id - 关联区域ID",
                "• violation_id - 关联违规ID",
                "• is_read - 是否已读",
                "• created_at - 创建时间",
            ],
        },
        {
            title: "第六章 API接口设计",
            content: [
                "6.1 摄像头管理接口",
                "",
                "• GET /api/cameras - 获取摄像头列表",
                "• POST /api/cameras - 添加摄像头",
                "• PUT /api/cameras/{id} - 更新摄像头",
                "• DELETE /api/cameras/{id} - 删除摄像头",
                "",
                "6.2 检测控制接口",
                "",
                "• POST /api/detection/start/{camera_id} - 启动检测",
                "• POST /api/detection/stop/{camera_id} - 停止检测",
                "• GET /api/detection/status - 获取检测状态",
                "• GET /api/detection/stream/{camera_id} - 获取视频流",
                "",
                "6.3 违规管理接口",
                "",
                "• GET /api/violations - 获取违规列表",
                "• GET /api/violations/{id} - 获取违规详情",
                "• PUT /api/violations/{id} - 更新违规备注",
                "• PUT /api/violations/{id}/process - 标记已处理",
                "• DELETE /api/violations/{id} - 删除违规记录",
                "• GET /api/violations/export - 导出Excel",
                "",
                "6.4 统计分析接口",
                "",
                "• GET /api/statistics/zone - 区域统计",
                "• GET /api/statistics/period - 时段统计",
                "• GET /api/statistics/trend - 趋势统计",
                "• GET /api/statistics/camera - 摄像头统计",
            ],
        },
        {
            title: "第七章 系统安全设计",
            content: [
                "7.1 身份认证",
                "",
                "• 用户名密码认证",
                "• Token会话管理",
                "• 登录失败限制",
                "",
                "7.2 权限控制",
                "",
                "• 基于角色的访问控制（RBAC）",
                "• 资源级权限控制",
                "• 操作审计日志",
                "",
                "7.3 数据安全",
                "",
                "• 数据定期备份",
                "• 敏感数据加密",
                "• 安全传输协议（HTTPS）",
            ],
        },
    ],
};

function createDesignDoc() {
    const children = [];

    // 标题页
    children.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 400 },
        children: [new TextRun({
            text: designDocContent.title,
            font: "SimHei",
            size: 44,
            bold: true,
        })],
    }));

    children.push(createParagraph("著作权人：（待填写）"));
    children.push(createParagraph("版本：1.0"));
    children.push(createParagraph("设计日期：2024年12月"));
    children.push(new Paragraph({ text: "" }));

    designDocContent.sections.forEach(section => {
        children.push(createTitle(section.title, 2));
        children.push(new Paragraph({ text: "" }));

        if (section.content) {
            section.content.forEach(line => {
                if (line.startsWith("• ")) {
                    children.push(createParagraph("  " + line));
                } else if (line.match(/^\d+\./) || line.startsWith("○")) {
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

Packer.toBuffer(createDesignDoc()).then(buffer => {
    const outputPath = "/Users/heqijie/个人项目/中烟软著/头盔/copyright-application-materials/设计说明书_模板版.docx";
    fs.writeFileSync(outputPath, buffer);
    console.log(`✓ 已生成: ${outputPath}`);
}).catch(err => {
    console.error("生成失败:", err);
});
