import argparse
# from TestAuto import run_test
from TestAuto.core.create_project import ProjectManage


def execute_from_command_line():
    parser = argparse.ArgumentParser(prog='TestAuto', description='---TestAuto使用命令参考---')
    # 创建项目运行的命令
    subparsers = parser.add_subparsers(title='Command', metavar="命令介绍:")

    createApi = subparsers.add_parser('createapi', help='创建api项目')
    createApi.add_argument('api_name', metavar='api_name', help="接口项目名称")
    createWeb = subparsers.add_parser('createweb', help='创建web项目')
    createWeb.add_argument('web_name', metavar='web_name', help="web项目名称")

    parser_run = subparsers.add_parser('run', help='运行项目', aliases=['R'])
    parser_run.add_argument('test_dir', metavar='test_dir', help='测试文件路径', default='.')
    # 添加版本号
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 2.0')
    # 获取参数
    args = parser.parse_args()
    print(args)
    if hasattr(args, "api_name"):
        # 创建项目
        ProjectManage.create_api(args.api_name)
    elif hasattr(args, "web_name"):
        # 创建项目
        ProjectManage.create_web(args.api_name)
    elif hasattr(args, "test_dir"):
        # 运行项目
        # run_test.main(args.test_dir)
        pass
    else:
        # 没有参数则打印帮助信息
        parser.print_help()


execute_from_command_line()
