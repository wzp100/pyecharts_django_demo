# """
# 自定义Django管理命令：自动统计各赛区和学校数据并缓存到JSON文件
# 用于周期性（如定时任务）自动维护统计缓存，提升系统自动化水平。
# """
# from django.core.management.base import BaseCommand
# from demo.views import get_area_stats, get_northwest_schools_stats, get_school_yearly_stats

# class Command(BaseCommand):
#     help = '自动统计各赛区和学校数据并缓存到JSON文件，可用于定时任务或手动执行'

#     def handle(self, *args, **kwargs):
#         updated_files = []
#         errors = []
#         for year in range(2019, 2024):
#             try:
#                 self.stdout.write(self.style.NOTICE(f"正在更新 {year} 年的数据..."))
#                 # 调用views中的统计与缓存函数
#                 get_area_stats(year)
#                 updated_files.append(f'area_stats_{year}.json')
#                 get_northwest_schools_stats(year)
#                 updated_files.append(f'northwest_schools_{year}.json')
#                 get_school_yearly_stats(year)
#                 updated_files.append(f'school_yearly_stats_{year}.json')
#                 self.stdout.write(self.style.SUCCESS(f"{year} 年数据更新完成."))
#             except Exception as e:
#                 error_msg = f"更新 {year} 年数据时出错: {e}"
#                 self.stderr.write(self.style.ERROR(error_msg))
#                 errors.append(error_msg)
#         # 输出汇总信息
#         if errors:
#             self.stderr.write(self.style.ERROR("部分年份数据更新失败:"))
#             for err in errors:
#                 self.stderr.write(self.style.ERROR(err))
#         else:
#             self.stdout.write(self.style.SUCCESS("所有年份 (2019-2023) 的JSON数据文件已成功更新！"))
#         self.stdout.write("成功更新的文件:\n" + "\n".join(updated_files))