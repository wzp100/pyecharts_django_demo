import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from demo.models import TeamMember

class Command(BaseCommand):
    help = "从 CSV 更新 TeamMember.member_type_detail"

    def add_arguments(self, parser):
        # 这里定义了一个位置参数，名字叫 csv_file
        parser.add_argument(
            'csv_file',
            type=str,
            help='CSV 文件路径，必须包含 member_code 和 member_type_detail 列'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # 一定要和上面 add_arguments 一致
        path = options.get('csv_file')
        if not path:
            self.stderr.write("❌ 请提供 CSV 文件路径（位置参数）！")
            return

        # 打印一下，确认一下
        self.stdout.write(f"🛠 正在读取 CSV：{path}")

        updated = 0
        missing = []

        with open(path, newline='', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        # 构造 member_code → 对象 的映射
        codes = [r.get('member_code') for r in rows]
        qs = TeamMember.objects.filter(member_code__in=codes)
        members = {m.member_code: m for m in qs}

        to_update = []
        for row in rows:
            code = row.get('member_code')
            detail = row.get('member_type_detail')
            obj = members.get(code)
            if obj:
                obj.member_type_detail = detail
                to_update.append(obj)
            else:
                missing.append(code)

        if to_update:
            TeamMember.objects.bulk_update(to_update, ['member_type_detail'], batch_size=200)
            updated = len(to_update)

        self.stdout.write(self.style.SUCCESS(
            f"✅ 更新完成：{updated} 条，未找到 {len(missing)} 条({missing})"
        ))
