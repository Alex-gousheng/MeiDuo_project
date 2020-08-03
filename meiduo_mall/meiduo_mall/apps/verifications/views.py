import random, logging
from django import http
from django.http import HttpResponse
from django.shortcuts import render

from django.views import View
from django_redis import get_redis_connection
from verifications.libs.captcha.captcha import captcha
from . import constants
from meiduo_mall.utils.response_code import RETCODE
from verifications.libs.yuntongxun.ccp_sms import CCP

# Create your views here.

logger = logging.getLogger('django')

class SMSCodeView(View):
    def get(self, request, mobile):
        # 接受参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')

        # 校验参数
        if not all([image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')

        # 提取图形验证码
        redis_conn = get_redis_connection('verify_code')
        image_code_server = redis_conn.get('img_%s' % uuid)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # 删除图形验证码
        redis_conn.delete('img_%s' % uuid)
        # 对比图形验证码
        image_code_server = image_code_server.decode()  # 将bytes转字符串，再比较
        if image_code_client.lower() != image_code_server.lower():  # 转小写，再比较
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 生成短信验证码：随机6位数字，000007
        sms_code = '%06d' % random.randint(0, 999999)
        logger.info(sms_code)  # 手动的输出日志，记录短信验证码
        # 保存短信验证码
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 创建redis管道
        

        # 将命令添加到队列中
        # 执行

        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60],
                                constants.SEND_SMS_TEMPLATE_ID)

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class ImageCodeView(View):
    def get(self, request, uuid):
        text, image = captcha.generate_captcha()

        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        return HttpResponse(image, content_type='image/jpg')