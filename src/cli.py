"""CLI 入口 - 命令行解析"""

import argparse
import sys
from typing import List


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog="mathgen",
        description="小学数学专题练习卷生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  mathgen generate-questions --all              生成全知识点题目
  mathgen generate-questions --grade 2           生成二年级题目
  mathgen generate-questions --kp "100以内进位加法" -n 50
  mathgen generate --kp "100以内进位加法" -n 20 --with-answer
  mathgen generate --grade 2 -n 50 --with-answer --with-error-tip
  mathgen extract 试卷.doc                        解析单个卷子
  mathgen batch 试卷文件夹/                      批量解析
  mathgen review                                 交互式审核
  mathgen query --kp "进位加法" --limit 10
  mathgen stats                                  统计报告
  mathgen import-error 错题.png                  导入错题
  mathgen error-practice -n 20                   错题专项练习
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # === generate-questions ===
    gq_parser = subparsers.add_parser("generate-questions", help="程序化生成题目")
    gq_parser.add_argument("--all", action="store_true", help="生成所有知识点题目")
    gq_parser.add_argument("--grade", type=str, help="指定年级（如：二年级）")
    gq_parser.add_argument("--kp", type=str, help="指定知识点名称")
    gq_parser.add_argument("-n", "--count", type=int, default=50, help="生成题目数量（默认50）")
    gq_parser.add_argument("--types", type=str, help="指定题型（逗号分隔）")

    # === generate ===
    gen_parser = subparsers.add_parser("generate", help="生成练习卷PDF")
    gen_parser.add_argument("--kp", type=str, help="知识点（逗号分隔）")
    gen_parser.add_argument("--grade", type=str, help="年级")
    gen_parser.add_argument("-n", "--count", type=int, default=50, help="题量")
    gen_parser.add_argument("--types", type=str, help="题型（逗号分隔）")
    gen_parser.add_argument("--with-answer", action="store_true", help="包含答案页")
    gen_parser.add_argument("--with-error-tip", action="store_true", help="包含易错提示")
    gen_parser.add_argument("--output", type=str, help="输出PDF路径")
    gen_parser.add_argument("--title", type=str, help="练习卷标题")

    # === extract ===
    ext_parser = subparsers.add_parser("extract", help="解析单个卷子")
    ext_parser.add_argument("file", type=str, help=".doc文件路径")

    # === batch ===
    batch_parser = subparsers.add_parser("batch", help="批量解析卷子")
    batch_parser.add_argument("folder", type=str, help="文件夹路径")
    batch_parser.add_argument("--recursive", action="store_true", help="递归子文件夹")

    # === review ===
    review_parser = subparsers.add_parser("review", help="交互式审核题目")
    review_parser.add_argument("--kp", type=str, help="按知识点筛选")
    review_parser.add_argument("--limit", type=int, default=50, help="每次显示数量")

    # === query ===
    query_parser = subparsers.add_parser("query", help="查询题库")
    query_parser.add_argument("--kp", type=str, help="知识点名称")
    query_parser.add_argument("--grade", type=str, help="年级")
    query_parser.add_argument("--type", type=str, help="题型")
    query_parser.add_argument("--difficulty", type=int, help="难度(1-5)")
    query_parser.add_argument("--status", type=str, default="approved", help="审核状态")
    query_parser.add_argument("--limit", type=int, default=20, help="返回数量")
    query_parser.add_argument("--json", action="store_true", dest="json_output", help="JSON格式输出")

    # === stats ===
    stats_parser = subparsers.add_parser("stats", help="统计报告")
    stats_parser.add_argument("--json", action="store_true", dest="json_output", help="JSON格式输出")

    # === import-error ===
    ie_parser = subparsers.add_parser("import-error", help="导入错题")
    ie_parser.add_argument("image", type=str, help="错题图片路径")
    ie_parser.add_argument("--kp", type=str, help="关联知识点")

    # === error-practice ===
    ep_parser = subparsers.add_parser("error-practice", help="错题专项练习")
    ep_parser.add_argument("-n", "--count", type=int, default=20, help="题量")
    ep_parser.add_argument("--output", type=str, help="输出PDF路径")
    ep_parser.add_argument("--with-answer", action="store_true", help="包含答案")

    # === config ===
    cfg_parser = subparsers.add_parser("config", help="配置管理")
    cfg_sub = cfg_parser.add_subparsers(dest="cfg_command")
    cfg_show = cfg_sub.add_parser("show", help="显示当前配置")
    cfg_set_model = cfg_sub.add_parser("set-model", help="设置LLM模型")
    cfg_set_model.add_argument("model", type=str, help="模型名称")
    cfg_set_key = cfg_sub.add_parser("set-api-key", help="设置API Key")
    cfg_set_key.add_argument("key", type=str, help="API Key")

    return parser


def main(argv: List[str] = None):
    """CLI 主入口"""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # 延迟导入，避免循环依赖
    from .cli_main import handle_command
    handle_command(args)


if __name__ == "__main__":
    main()
