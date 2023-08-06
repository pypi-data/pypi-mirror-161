from django.db import models


# Create your models here.


# 9、User_Permission 权限表 [1-N]
class Permission(models.Model):
    permission_id = models.IntegerField(verbose_name='权限ID', primary_key=True, help_text='必填。不自动生成，由运营人员统一设置。')
    permission_name = models.CharField(verbose_name='权限名称', max_length=255, blank=True, null=True, )

    class Meta:
        db_table = 'user_permission'
        verbose_name_plural = "09. 用户 - 权限类型表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.permission_name}"


# 10、User_Permission_Value 权限值表 [1-N]
# 权限标识值，一个permission_id可以对应多个value，多值形成一组权限。值为宏名，需要多语言翻译
class PermissionValue(models.Model):
    permission = models.ForeignKey(Permission, verbose_name='权限ID', on_delete=models.DO_NOTHING, )
    value = models.CharField(verbose_name='权限值', max_length=255, blank=True, null=True, )
    is_system = models.BooleanField(verbose_name='是否系统权限', blank=True, null=True, )
    is_ban = models.BooleanField(verbose_name='是否禁用', blank=True, null=True, )

    class Meta:
        db_table = 'user_permission_value'
        verbose_name_plural = "10. 用户 - 权限详细表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.value}"


# 11、User_Group 分组表
class Group(models.Model):
    id = models.IntegerField(verbose_name='ID', primary_key=True, auto_created=True)
    # xj_user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    group = models.CharField(verbose_name='用户组', max_length=32, blank=True, null=True, )
    parent_group = models.CharField(verbose_name='父组', max_length=32, blank=True, null=True, )
    description = models.CharField(verbose_name='描述', max_length=32, blank=True, null=True, )

    # permission = models.ForeignKey(Permission, verbose_name='权限ID', on_delete=models.DO_NOTHING, blank=True, null=True, )

    class Meta:
        db_table = 'user_group'
        verbose_name_plural = "11. 用户 - 分组表"

    def __str__(self):
        return f"{self.description}"


# 1、User_Base_Info 基础信息表 [NF1]
class BaseInfo(models.Model):
    # platform_uid = models.BigIntegerField(verbose_name='平台用户ID', db_index=True)
    # platform = models.ForeignKey(Platform, on_delete=models.DO_NOTHING, verbose_name='平台ID',)
    user_name = models.CharField(verbose_name='用户名', max_length=128, blank=True, null=True, db_index=True)
    full_name = models.CharField(verbose_name='姓名', max_length=128, blank=True, null=True, db_index=True)
    nickname = models.CharField(verbose_name='昵称', max_length=128, blank=True, null=True)
    phone = models.CharField(verbose_name='手机', max_length=128, blank=True, null=True, db_index=True)
    email = models.EmailField(verbose_name='邮箱', blank=True, null=True, db_index=True)
    wechat = models.CharField(verbose_name='微信号', max_length=128, blank=True, null=True, db_index=True)
    user_info = models.JSONField(verbose_name='用户信息', blank=True, null=True)
    user_group = models.ForeignKey(Group, verbose_name='用户分组', blank=True, null=True, on_delete=models.DO_NOTHING)
    permission = models.ForeignKey(Permission, verbose_name='用户权限', blank=True, null=True, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'user_base_info'
        # unique_together = [['platform', 'platform_uid'], ['platform', 'user_name']]
        verbose_name_plural = "01. 用户 - 基础信息"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.full_name}"

    def get_group_desc(self):
        return self.user_group.description if self.user_group else ""

    def get_permission_desc(self):
        return self.permission.permission_name if self.permission else ""


# 2、User_Auth 认证表 [1-1]
class Auth(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    password = models.CharField(verbose_name='密码', max_length=255, blank=True, null=True, )
    plaintext = models.CharField(verbose_name='PT', max_length=255, blank=True, null=True, )
    salt = models.CharField(verbose_name='盐', max_length=32, blank=True, null=True, )
    algorithm = models.CharField(verbose_name='加密算法', max_length=255, blank=True, null=True, )
    token = models.CharField(verbose_name='临时凭证', max_length=255, blank=True, null=True, )
    ticket = models.CharField(verbose_name='临时票据', max_length=255, blank=True, null=True, )
    create_time = models.DateTimeField(verbose_name='密码创建时间', auto_now_add=True, )
    update_time = models.DateTimeField(verbose_name='凭证更新时间', auto_now=True, blank=True, null=True, )

    class Meta:
        db_table = 'user_auth'
        verbose_name_plural = "02. 用户 - 安全认证"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.user.user_name}"


# 3、User_Detail_Info 详细信息表 [1-1]
class DetailInfo(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    real_name = models.CharField(verbose_name='真实姓名', max_length=255, blank=True, null=True, db_index=True, )
    sex = models.CharField(verbose_name='性别', max_length=1, blank=True, null=True, )
    birth = models.DateField(verbose_name='生日', blank=True, null=True, )
    tags = models.CharField(verbose_name='个人标签', max_length=255, blank=True, null=True, )
    signature = models.CharField(verbose_name='个性签名', max_length=255, blank=True, null=True, )
    avatar = models.CharField(verbose_name='个人头像', max_length=255, blank=True, null=True, )
    cover = models.CharField(verbose_name='个人封面', max_length=255, blank=True, null=True, )
    language = models.CharField(verbose_name='语言', max_length=32, blank=True, null=True, )
    region_code = models.BigIntegerField(verbose_name='地区编码', blank=True, null=True, db_index=True, )
    more = models.JSONField(verbose_name='更多信息', max_length=255, blank=True, null=True, )
    field_1 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_2 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_3 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_4 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_5 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_6 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_7 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_8 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_9 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_10 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_11 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_12 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_13 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_14 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )
    field_15 = models.CharField(verbose_name='信息', max_length=255, blank=True, null=True, )

    class Meta:
        db_table = 'user_detail_info'
        verbose_name_plural = "03. 用户 - 详细信息"

    def __str__(self):
        # return f"{self.user_name}({self.real_name})"
        return f"{self.user.user_name}"


class ExtendFiled(models.Model):
    field = models.CharField(verbose_name='字段名称', max_length=255, blank=True, null=True, db_index=True, )
    key_name = models.CharField(verbose_name='标签映射', max_length=255, blank=True, null=True, )
    description = models.CharField(verbose_name='字段描述', max_length=255, blank=True, null=True, )

    class Meta:
        db_table = 'user_extend_field'
        verbose_name_plural = "04. 用户 - 冗余扩展表"

    def __str__(self):
        return f"{self.key_name}"


# 4、*User_Access_Log 访问日志表 [1-N]
class AccessLog(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    ip = models.CharField(verbose_name='IP', max_length=128, blank=True, null=True, )
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, )
    client_info = models.JSONField(verbose_name='客户端信息', blank=True, null=True, )
    more = models.JSONField(verbose_name='更多信息', max_length=255, blank=True, null=True, )

    class Meta:
        db_table = 'user_access_log'
        verbose_name_plural = "04. 用户 - 访问日志表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.user.user_name}"


# 5、*User_History 操作历史表 [1-N]
class History(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    field = models.CharField(verbose_name='操作字段', max_length=32, blank=True, null=True, )
    old_value = models.CharField(verbose_name='旧值', max_length=255, blank=True, null=True, )
    new_value = models.CharField(verbose_name='新值', max_length=255, blank=True, null=True, )
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, )

    class Meta:
        db_table = 'user_history'
        verbose_name_plural = "05. 用户 - 操作历史表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.user.user_name}"


# 6、*User_Restrict_Region 限制范围表
class RestrictRegion(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, )
    region_code = models.BigIntegerField(verbose_name='允许的地区编码', blank=True, null=True, db_index=True, )

    class Meta:
        db_table = 'user_restrict_region'
        verbose_name_plural = "06. 用户 - 限制范围表"

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.user.user_name}"


# 7、*User_Platform 平台表
class Platform(models.Model):
    platform_id = models.IntegerField(verbose_name='平台ID', primary_key=True, help_text='必填。不自动生成，由运营人员统一设置。')
    platform_name = models.CharField(verbose_name='平台名称', max_length=128, help_text='必填。平台名称可以是中文、英文、俄文等。')
    platforms_to_users = models.ManyToManyField(BaseInfo, through='PlatformsToUsers', )

    class Meta:
        db_table = 'user_platform'
        verbose_name_plural = "07. 用户 - 平台表"

    def __str__(self):
        return f"{self.platform_name}"

    # 以上代码执行的Sql语句
    # CREATE TABLE `user_platform`(`platform_id` integer NOT NULL PRIMARY KEY, `platform_name` varchar(128) NOT NULL);


# 8、*User_Platforms_To_Users - 多对多平台记录表 [N-N]
class PlatformsToUsers(models.Model):
    user = models.ForeignKey(BaseInfo, verbose_name='用户', on_delete=models.DO_NOTHING, db_column='user_id')
    platform = models.ForeignKey(Platform, verbose_name='平台', on_delete=models.DO_NOTHING, )
    platform_user_id = models.BigIntegerField(verbose_name='平台用户ID', blank=True, null=True, db_index=True, )

    class Meta:
        db_table = 'user_platforms_to_users'
        verbose_name_plural = "08. 用户 - 多对多平台记录表"
        managed = False

    def __str__(self):
        # return f"{self.user_name}({self.full_name})"
        return f"{self.user.user_name}"
